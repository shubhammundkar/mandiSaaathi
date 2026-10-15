// Mandi Saathi - Voice Service (Web Speech API)
// Implements SpeechRecognition (mr-IN, hi-IN, en-IN) with live transcript
// and speechSynthesis with Marathi priority, Devanagari fallback, and mute control.

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
    const clean = (lang || 'mr').toLowerCase();
    if (clean.startsWith('mr')) return 'mr-IN';
    if (clean.startsWith('hi')) return 'hi-IN';
    return 'en-IN';
  }

  // Helper: Find appropriate speech synthesis voice with priority for Marathi
  getVoiceForLanguage(lang) {
    const bcpTag = this.getBcp47Tag(lang);
    if (!this.availableVoices.length && 'speechSynthesis' in window) {
      this._loadVoices();
    }

    const voices = this.availableVoices;
    if (!voices.length) return null;

    // 1. Marathi request
    if (bcpTag === 'mr-IN') {
      // Direct Marathi voice (by language tag or name)
      const mrVoice = voices.find((v) => {
        const l = v.lang.toLowerCase().replace('_', '-');
        const n = v.name.toLowerCase();
        return l.startsWith('mr') || n.includes('marathi') || n.includes('मराठी') || n.includes('hemant');
      });
      if (mrVoice) return mrVoice;

      // High-quality Devanagari Hindi voice fallback (pronounced with identical Devanagari phonetics)
      const hiVoice = voices.find((v) => {
        const l = v.lang.toLowerCase().replace('_', '-');
        const n = v.name.toLowerCase();
        return l.startsWith('hi') || n.includes('hindi') || n.includes('हिन्दी') || n.includes('kalpana') || n.includes('swara');
      });
      if (hiVoice) {
        console.info('Using Devanagari voice for Marathi TTS:', hiVoice.name);
        return hiVoice;
      }
    }

    // 2. Hindi request
    if (bcpTag === 'hi-IN') {
      const hiVoice = voices.find((v) => {
        const l = v.lang.toLowerCase().replace('_', '-');
        const n = v.name.toLowerCase();
        return l.startsWith('hi') || n.includes('hindi') || n.includes('हिन्दी');
      });
      if (hiVoice) return hiVoice;
    }

    // 3. English or general fallback
    const enVoice = voices.find((v) => {
      const l = v.lang.toLowerCase().replace('_', '-');
      return l.startsWith('en-in') || l.startsWith('en');
    });
    return enVoice || voices[0] || null;
  }

  // Helper: Get user-friendly error message in specified language
  getLocalizedErrorMessage(errCode, lang = 'mr') {
    if (lang === 'mr') {
      switch (errCode) {
        case 'not-allowed':
        case 'permission-denied':
          return 'मायक्रोफोन परवानगी मिळालेली नाही. कृपया ब्राऊझर सेटिंग्जमध्ये मायक्रोफोन सुरू करा किंवा खाली टाईप करा.';
        case 'audio-capture':
          return 'मायक्रोफोन आढळला नाही. कृपया माईक तपासा किंवा खाली टाईप करा.';
        case 'network':
          return 'इंटरनेट नेटवर्क अडचण आली आहे. कृपया इंटरनेट तपासा किंवा टाईप करा.';
        case 'no-speech':
          return 'काही आवाज ऐकू आला नाही. कृपया पुन्हा माईक दाबून बोला.';
        default:
          return 'आवाज ओळखण्यात अडचण आली. कृपया खाली टाईप करा.';
      }
    } else if (lang === 'hi') {
      switch (errCode) {
        case 'not-allowed':
        case 'permission-denied':
          return 'माइक्रोफ़ोन की अनुमति नहीं मिली। कृपया ब्राउज़र सेटिंग्स में अनुमति दें या नीचे टाइप करें।';
        case 'no-speech':
          return 'कोई आवाज़ सुनाई नहीं दी। कृपया फिर से बोलें।';
        default:
          return 'आवाज़ पहचानने में समस्या हुई। कृपया नीचे टाइप करें।';
      }
    } else {
      switch (errCode) {
        case 'not-allowed':
        case 'permission-denied':
          return 'Microphone permission denied. Please allow microphone access or type below.';
        case 'no-speech':
          return 'No speech detected. Please tap mic again to speak.';
        default:
          return 'Speech recognition error. You can type below.';
      }
    }
  }

  // --- Speech Recognition ---

  startListening({
    lang = 'mr',
    onInterim = () => {},
    onFinal = () => {},
    onError = () => {},
    onStart = () => {},
    onEnd = () => {}
  } = {}) {
    if (!this.isRecognitionSupported()) {
      const errMsg = this.getLocalizedErrorMessage('not-supported', lang);
      onError({ error: 'not-supported', message: errMsg });
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
        const friendlyMessage = this.getLocalizedErrorMessage(event.error, lang);
        onError({ error: event.error, message: friendlyMessage });
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
      const friendlyMessage = this.getLocalizedErrorMessage('start-failure', lang);
      onError({ error: 'start-failure', message: friendlyMessage });
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

  speak(text, lang = 'mr', { onStart = () => {}, onEnd = () => {}, onError = () => {} } = {}) {
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

    // Clean text and translate symbols into natural spoken Marathi
    let cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/#+\s+/g, '')
      .replace(/[•\-\*]\s+/g, '')
      .replace(/-₹/g, ' वजा रुपये ')
      .replace(/\+₹/g, ' अधिक रुपये ')
      .replace(/₹/g, ' रुपये ')
      .replace(/\/क्विंटल|\/q|\/ क्विंटल/g, ' प्रति क्विंटल ')
      .replace(/किमी/g, ' किलोमीटर ')
      .replace(/%/g, ' टक्के ')
      .replace(/[\(\)]/g, ' ')
      .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '') // Remove emojis
      .replace(/\s+/g, ' ')
      .trim();

    if (!cleanText) {
      onEnd();
      return;
    }

    try {
      const bcpTag = this.getBcp47Tag(lang);
      const voice = this.getVoiceForLanguage(lang);

      const utterance = new SpeechSynthesisUtterance(cleanText);
      // Ensure utterance.lang matches the voice language to prevent browser speech rejection
      utterance.lang = voice && voice.lang ? voice.lang : bcpTag;
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
