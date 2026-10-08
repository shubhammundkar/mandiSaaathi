// Mandi Saathi - Voice Service (Web Speech API)
// Implements SpeechRecognition (en-IN, hi-IN, mr-IN) with live transcript
// and speechSynthesis with mute toggle, falling back to a hi-IN voice if no Marathi voice.

const SpeechRecClass = window.SpeechRecognition || window.webkitSpeechRecognition || null;
const MUTE_STORAGE_KEY = 'mandisaathi_voice_muted';

class VoiceService {
  constructor() {
    this.recognition = null;
    this._isListening = false;
    this._isSpeaking = false;
    this._isMuted = localStorage.getItem(MUTE_STORAGE_KEY) === 'true';
    this.availableVoices = [];

    // Pre-cache voices when available
    if ('speechSynthesis' in window) {
      this._loadVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => this._loadVoices();
      }
    }
  }

  _loadVoices() {
    if ('speechSynthesis' in window) {
      this.availableVoices = window.speechSynthesis.getVoices() || [];
    }
  }

  // --- Capabilities Detection ---

  isRecognitionSupported() {
    return Boolean(SpeechRecClass);
  }

  isSynthesisSupported() {
    return 'speechSynthesis' in window;
  }

  isListening() {
    return this._isListening;
  }

  isSpeaking() {
    return this._isSpeaking;
  }

  isMuted() {
    return this._isMuted;
  }

  toggleMute() {
    this._isMuted = !this._isMuted;
    localStorage.setItem(MUTE_STORAGE_KEY, String(this._isMuted));
    if (this._isMuted) {
      this.stopSpeaking();
    }
    return this._isMuted;
  }

  setMute(muted) {
    this._isMuted = Boolean(muted);
    localStorage.setItem(MUTE_STORAGE_KEY, String(this._isMuted));
    if (this._isMuted) {
      this.stopSpeaking();
    }
  }

  // Helper: Map app language code ('en', 'hi', 'mr') to BCP 47 tag
  getBcp47Tag(lang) {
    const clean = (lang || 'en').toLowerCase();
    if (clean.startsWith('mr')) return 'mr-IN';
    if (clean.startsWith('hi')) return 'hi-IN';
    return 'en-IN';
  }

  // Helper: Find appropriate speech synthesis voice with fallback
  getVoiceForLanguage(lang) {
    const bcpTag = this.getBcp47Tag(lang);
    if (!this.availableVoices.length && 'speechSynthesis' in window) {
      this._loadVoices();
    }

    const voices = this.availableVoices;
    if (!voices.length) return null;

    // 1. Marathi request
    if (bcpTag === 'mr-IN') {
      // Direct Marathi voice
      const mrVoice = voices.find((v) => v.lang.toLowerCase().replace('_', '-').startsWith('mr'));
      if (mrVoice) return mrVoice;

      // Fallback: hi-IN voice if no Marathi voice is available in the browser/OS
      const hiVoice = voices.find((v) => v.lang.toLowerCase().replace('_', '-').startsWith('hi'));
      if (hiVoice) {
        console.info('No mr-IN voice found in system; falling back to hi-IN voice:', hiVoice.name);
        return hiVoice;
      }
    }

    // 2. Hindi request
    if (bcpTag === 'hi-IN') {
      const hiVoice = voices.find((v) => v.lang.toLowerCase().replace('_', '-').startsWith('hi'));
      if (hiVoice) return hiVoice;
    }

    // 3. English or general fallback
    const enVoice = voices.find((v) => v.lang.toLowerCase().replace('_', '-').startsWith('en-in') || v.lang.toLowerCase().startsWith('en'));
    return enVoice || voices[0] || null;
  }

  // --- Speech Recognition ---

  startListening({
    lang = 'en',
    onInterim = () => {},
    onFinal = () => {},
    onError = () => {},
    onStart = () => {},
    onEnd = () => {}
  } = {}) {
    if (!this.isRecognitionSupported()) {
      onError({ error: 'not-supported', message: 'Speech recognition is not supported in this browser.' });
      return false;
    }

    if (this._isListening) {
      this.stopListening();
    }

    try {
      this.recognition = new SpeechRecClass();
      const bcpTag = this.getBcp47Tag(lang);
      this.recognition.lang = bcpTag;
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;

      let finalTranscript = '';

      this.recognition.onstart = () => {
        this._isListening = true;
        onStart();
      };

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i];
          if (item.isFinal) {
            finalTranscript += item[0].transcript;
          } else {
            interimTranscript += item[0].transcript;
          }
        }

        if (interimTranscript) {
          onInterim(interimTranscript);
        }
        if (finalTranscript) {
          onFinal(finalTranscript.trim());
        }
      };

      this.recognition.onerror = (event) => {
        this._isListening = false;
        console.warn('SpeechRecognition error:', event.error);
        onError(event);
      };

      this.recognition.onend = () => {
        this._isListening = false;
        onEnd();
      };

      this.recognition.start();
      return true;
    } catch (err) {
      console.error('Failed to start SpeechRecognition:', err);
      this._isListening = false;
      onError({ error: 'start-failure', message: err.message });
      return false;
    }
  }

  stopListening() {
    if (this.recognition && this._isListening) {
      try {
        this.recognition.stop();
      } catch (_) {}
    }
    this._isListening = false;
  }

  // --- Speech Synthesis ---

  speak(text, lang = 'en', { onStart = () => {}, onEnd = () => {}, onError = () => {} } = {}) {
    if (!this.isSynthesisSupported()) {
      onError({ error: 'not-supported', message: 'Speech synthesis not supported.' });
      return;
    }

    // If muted, do not produce sound; fire onEnd immediately
    if (this._isMuted) {
      onEnd();
      return;
    }

    this.stopSpeaking();

    // Clean markdown asterisks, hashes, and formatting for clean voice reading
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/#+\s+/g, '')
      .replace(/[•\-\*]\s+/g, '')
      .replace(/₹/g, 'रुपये ')
      .trim();

    if (!cleanText) {
      onEnd();
      return;
    }

    try {
      const bcpTag = this.getBcp47Tag(lang);
      const voice = this.getVoiceForLanguage(lang);

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = bcpTag;
      if (voice) {
        utterance.voice = voice;
      }
      utterance.rate = 0.95;
      utterance.pitch = 1.0;

      utterance.onstart = () => {
        this._isSpeaking = true;
        onStart();
      };

      utterance.onend = () => {
        this._isSpeaking = false;
        onEnd();
      };

      utterance.onerror = (err) => {
        this._isSpeaking = false;
        console.warn('SpeechSynthesis error:', err);
        onError(err);
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error('Speech synthesis execution failed:', err);
      this._isSpeaking = false;
      onError(err);
    }
  }

  stopSpeaking() {
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (_) {}
    }
    this._isSpeaking = false;
  }
}

export const voice = new VoiceService();
export default voice;
