// Mandi Saathi - Chat Page (Voice & Multilingual AI Chat Advisor)
// WhatsApp-style bubbles in pastel green theme, quick-reply chips,
// large mic button with pulse animation, mini result cards inside chat,
// and Web Speech API integration with graceful fallbacks.

import { t, getLanguage } from '../i18n.js';
import { api } from '../api.js';
import { voice } from '../voice.js';

// Initial conversation history
const initialMessages = [
  {
    sender: 'bot',
    text: null, // Will be set dynamically by language
    data: null,
    time: formatTime(new Date())
  }
];

const state = {
  messages: [...initialMessages],
  isRecording: false,
  isSending: false,
  liveTranscript: '',
  sessionId: 'session-' + Math.random().toString(36).substring(2, 9)
};

function formatTime(d) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function render(container) {
  const currentLang = getLanguage();
  const isSpeechRecSupported = voice.isRecognitionSupported();
  const isMuted = voice.isMuted();

  // Set default welcome message if first message has no text yet
  if (!state.messages[0].text) {
    if (currentLang === 'mr') {
      state.messages[0].text = "नमस्कार शेतकरी मित्रांनो! मी **मंडी साथी** आहे. तुम्हाला कोणत्या पिकाचे बाजारभाव, विक्रीसाठी सर्वोत्तम मंडी किंवा साठवणुकीचा सल्ला हवा आहे? खालील बटण दाबून बोला किंवा लिहा.";
    } else if (currentLang === 'hi') {
      state.messages[0].text = "नमस्ते किसान भाइयो! मैं **मंडी साथी** हूँ। आपको किस फसल का मंडी भाव, सबसे अच्छी बिक्री मंडी या भंडारण सलाह चाहिए? बोलकर या लिखकर पूछें।";
    } else {
      state.messages[0].text = "Hello farmer friends! I am **Mandi Saathi**. Ask me about the best mandi to sell your harvest, today's prices, or storage timing. Speak or type below!";
    }
  }

  container.innerHTML = `
    <div class="container" style="max-width: 860px; padding: 0 12px;">
      
      <!-- Chat Outer Window -->
      <div class="chat-window">
        
        <!-- Chat Header -->
        <div class="chat-header">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 42px; height: 42px; border-radius: 50%; background: var(--primary-light); color: var(--primary-dark); display: flex; align-items: center; justify-content: center; font-weight: 700;">
              <i data-lucide="bot" style="width: 24px; height: 24px;"></i>
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text); font-size: 1.05rem;" data-i18n="chat_title">
                ${t('chat_title')}
              </div>
              <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #2E7D32;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #4CAF50; display: inline-block;"></span>
                <span>Active APMC Engine • ${currentLang.toUpperCase()}</span>
              </div>
            </div>
          </div>

          <!-- Mute Audio Voice Toggle Button -->
          <div style="display: flex; align-items: center; gap: 8px;">
            <button type="button" class="btn btn-ghost" id="btn-toggle-mute" style="border-radius: var(--radius-pill); padding: 6px 12px; font-size: 0.8rem; height: 36px; border: 1px solid var(--border);" title="${isMuted ? t('chat_unmute_voice') : t('chat_mute_voice')}">
              <i data-lucide="${isMuted ? 'volume-x' : 'volume-2'}" style="width: 16px; height: 16px;"></i>
              <span id="mute-btn-label">${isMuted ? t('chat_unmute_voice') : t('chat_mute_voice')}</span>
            </button>
          </div>
        </div>

        <!-- Speech Not Supported Notice (if browser lacks SpeechRecognition) -->
        ${!isSpeechRecSupported ? `
          <div style="background: #FFF9C4; border-bottom: 1px solid #FFF176; padding: 8px 16px; font-size: 0.82rem; color: #827717; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="info" style="width: 16px; height: 16px; flex-shrink: 0;"></i>
            <span data-i18n="chat_voice_unsupported">${t('chat_voice_unsupported')}</span>
          </div>
        ` : ''}

        <!-- Chat Messages Flow Container -->
        <div class="chat-messages" id="chat-messages-container">
          ${renderMessagesHtml(state.messages)}
        </div>

        <!-- Live Voice Transcript Banner (Shown while speaking) -->
        <div class="live-transcript-banner" id="live-transcript-banner" style="display: ${state.isRecording ? 'flex' : 'none'};">
          <span style="width: 10px; height: 10px; border-radius: 50%; background: #E53935; display: inline-block; animation: mic-pulse 1s infinite;"></span>
          <span style="font-weight: 600;" data-i18n="chat_listening">${t('chat_listening')}</span>
          <span id="live-transcript-text" style="font-style: italic; color: #424242; margin-left: 4px;">
            ${state.liveTranscript || '...'}
          </span>
        </div>

        <!-- Quick Reply Chips -->
        <div class="chat-quick-chips">
          <button type="button" class="quick-chip" data-query="${t('chat_quick_1')}">
            <span>🍅</span>
            <span>${t('chat_quick_1')}</span>
          </button>
          <button type="button" class="quick-chip" data-query="${t('chat_quick_2')}">
            <span>🧅</span>
            <span>${t('chat_quick_2')}</span>
          </button>
          <button type="button" class="quick-chip" data-query="${t('chat_quick_3')}">
            <span>📊</span>
            <span>${t('chat_quick_3')}</span>
          </button>
          <button type="button" class="quick-chip" data-query="${t('chat_quick_4')}">
            <span>🥣</span>
            <span>${t('chat_quick_4')}</span>
          </button>
        </div>

        <!-- Chat Input Bar -->
        <form class="chat-input-bar" id="chat-form" onsubmit="return false;">
          <input 
            type="text" 
            id="chat-input" 
            class="input" 
            placeholder="${t('chat_input_placeholder')}" 
            autocomplete="off"
            style="min-height: 46px; border-radius: var(--radius-pill); font-size: 0.95rem; padding: 8px 18px;"
          />
          
          <!-- Send Button -->
          <button type="submit" class="btn btn-primary" id="btn-send-chat" style="width: 46px; height: 46px; min-width: 46px; padding: 0; border-radius: 50%;" title="Send">
            <i data-lucide="send" style="width: 18px; height: 18px;"></i>
          </button>

          <!-- Large Mic Button with Pulse Animation -->
          ${isSpeechRecSupported ? `
            <button type="button" class="btn-mic ${state.isRecording ? 'recording' : ''}" id="btn-voice-mic" title="Voice Search (Marathi / Hindi / English)">
              <i data-lucide="${state.isRecording ? 'square' : 'mic'}" style="width: 22px; height: 22px;"></i>
            </button>
          ` : ''}
        </form>

      </div>
    </div>
  `;

  // Attach event handlers
  bindEvents(container);

  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Scroll to bottom of message flow
  scrollToBottom(container);
}

// Format message bubbles HTML
function renderMessagesHtml(messages) {
  return messages.map((msg) => {
    const isUser = msg.sender === 'user';
    const formattedText = formatMessageText(msg.text);

    return `
      <div class="chat-message-row ${isUser ? 'user' : 'bot'}">
        <div class="chat-bubble ${isUser ? 'user' : 'bot'}">
          <div style="white-space: pre-line;">${formattedText}</div>
          
          <!-- Embedded Mini Result Card (If bot message contains structured engine data) -->
          ${!isUser && msg.data ? renderMiniResultCard(msg.data, msg.intent) : ''}

          <!-- Bubble Meta: Time & Voice Re-play -->
          <div class="chat-bubble-meta">
            ${!isUser ? `
              <button type="button" class="btn-bubble-listen" data-text="${escapeAttr(msg.text)}" style="background: none; border: none; cursor: pointer; color: #667781; display: inline-flex; align-items: center; margin-right: 6px;" title="Listen to message">
                <i data-lucide="volume-2" style="width: 14px; height: 14px;"></i>
              </button>
            ` : ''}
            <span>${msg.time}</span>
            ${isUser ? `<i data-lucide="check-check" style="width: 14px; height: 14px; color: #53BDEB;"></i>` : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Convert markdown-style **bold** and bullet points into HTML
function formatMessageText(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function escapeAttr(str) {
  if (!str) return '';
  return str.replace(/"/g, '&quot;');
}

// Render Mini Result Cards inside Bot Bubble
function renderMiniResultCard(data, intent) {
  if (!data) return '';

  // 1. Best Market Mini Card
  if (intent === 'best_market' && data.best_recommendation) {
    const b = data.best_recommendation;
    return `
      <div class="chat-mini-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <div style="display: flex; align-items: center; gap: 6px;">
            <span class="badge badge-green" style="font-size: 0.72rem; padding: 2px 8px;">Top Choice</span>
            <strong style="color: var(--text);">${b.market}</strong>
            <span style="font-size: 0.8rem; color: var(--muted);">(${b.district})</span>
          </div>
          <span style="font-size: 0.8rem; color: #2E7D32; font-weight: 700;">
            ₹${b.net_return_per_quintal.toFixed(2)}/q
          </span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.8rem; margin: 8px 0; background: #FFFFFF; padding: 8px; border-radius: 6px; border: 1px solid var(--border);">
          <div>Gross: <strong>₹${b.gross_modal_price.toFixed(0)}</strong></div>
          <div>Freight: <strong style="color: #C62828;">-₹${b.costs.transport_per_q.toFixed(2)}</strong></div>
          <div>Total Profit: <strong style="color: #2E7D32;">₹${b.total_net_earnings.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</strong></div>
          <div>Distance: <strong>${b.distance_km} km</strong></div>
        </div>

        <a href="#/advisor" class="btn btn-primary" style="width: 100%; height: 34px; font-size: 0.82rem; padding: 0;" data-i18n="chat_view_in_advisor">
          ${t('chat_view_in_advisor')}
        </a>
      </div>
    `;
  }

  // 2. Storage Decision Mini Card
  if (intent === 'store_or_sell' && data.recommendation) {
    const isSell = data.recommendation.toLowerCase().includes('sell');
    return `
      <div class="chat-mini-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <span class="badge ${isSell ? 'badge-yellow' : 'badge-green'}" style="font-size: 0.75rem;">
            ${data.recommendation}
          </span>
          <span style="font-size: 0.82rem; font-weight: 600;">
            Current: ₹${(data.current_price || 0).toFixed(0)}/q
          </span>
        </div>
        <p style="font-size: 0.82rem; color: var(--muted); margin: 4px 0 0;">
          ${data.rationale || ''}
        </p>
      </div>
    `;
  }

  // 3. Price Check Mini Card
  if (intent === 'price_check' && data.modal_price) {
    return `
      <div class="chat-mini-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <strong>${data.market} (${data.district})</strong>
          <span style="font-weight: 700; color: #2E7D32; font-size: 1rem;">
            ₹${data.modal_price.toFixed(0)}/q
          </span>
        </div>
        <div style="display: flex; gap: 12px; font-size: 0.78rem; color: var(--muted);">
          <span>Min: ₹${(data.min_price || 0).toFixed(0)}</span>
          <span>Max: ₹${(data.max_price || 0).toFixed(0)}</span>
          <span>Date: ${data.arrival_date || 'Today'}</span>
        </div>
      </div>
    `;
  }

  return '';
}

function scrollToBottom(container) {
  const msgDiv = container.querySelector('#chat-messages-container');
  if (msgDiv) {
    msgDiv.scrollTop = msgDiv.scrollHeight;
  }
}

// Bind all interactive controls
function bindEvents(container) {
  const form = container.querySelector('#chat-form');
  const input = container.querySelector('#chat-input');
  const btnMic = container.querySelector('#btn-voice-mic');
  const btnToggleMute = container.querySelector('#btn-toggle-mute');
  const liveBanner = container.querySelector('#live-transcript-banner');
  const liveText = container.querySelector('#live-transcript-text');

  // Submit via Enter or Send Button
  if (form && input) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (text) {
        input.value = '';
        handleSendMessage(text, container);
      }
    });
  }

  // Quick Reply Chips
  container.querySelectorAll('.quick-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-query');
      if (q) {
        handleSendMessage(q, container);
      }
    });
  });

  // Mute Voice Toggle
  if (btnToggleMute) {
    btnToggleMute.addEventListener('click', () => {
      const nowMuted = voice.toggleMute();
      const label = container.querySelector('#mute-btn-label');
      if (label) {
        label.textContent = nowMuted ? t('chat_unmute_voice') : t('chat_mute_voice');
      }
      const icon = btnToggleMute.querySelector('i');
      if (icon) {
        icon.setAttribute('data-lucide', nowMuted ? 'volume-x' : 'volume-2');
        if (window.lucide) window.lucide.createIcons();
      }
      if (window.showToast) {
        window.showToast(nowMuted ? 'Voice speech muted' : 'Voice speech unmuted', 'info');
      }
    });
  }

  // Large Mic Button Click Handler
  if (btnMic) {
    btnMic.addEventListener('click', () => {
      if (voice.isListening()) {
        // Stop recording if already listening
        voice.stopListening();
        setRecordingState(false, container);
      } else {
        // Start speech recognition in current language (mr-IN, hi-IN, en-IN)
        const lang = getLanguage();
        setRecordingState(true, container);

        voice.startListening({
          lang,
          onStart: () => {
            setRecordingState(true, container);
          },
          onInterim: (interim) => {
            state.liveTranscript = interim;
            if (liveText) liveText.textContent = interim;
          },
          onFinal: (finalText) => {
            setRecordingState(false, container);
            if (finalText && finalText.trim()) {
              handleSendMessage(finalText.trim(), container);
            }
          },
          onError: (err) => {
            setRecordingState(false, container);
            if (err.error !== 'no-speech' && window.showToast) {
              window.showToast(`Microphone notice: ${err.error || 'speech failed'}`, 'info');
            }
          },
          onEnd: () => {
            setRecordingState(false, container);
          }
        });
      }
    });
  }

  // Re-listen audio buttons on bot bubbles
  container.querySelectorAll('.btn-bubble-listen').forEach((btn) => {
    btn.addEventListener('click', () => {
      const rawText = btn.getAttribute('data-text');
      if (rawText) {
        voice.speak(rawText, getLanguage());
      }
    });
  });
}

function setRecordingState(isRec, container) {
  state.isRecording = isRec;
  const btnMic = container.querySelector('#btn-voice-mic');
  const liveBanner = container.querySelector('#live-transcript-banner');
  const liveText = container.querySelector('#live-transcript-text');

  if (btnMic) {
    if (isRec) {
      btnMic.classList.add('recording');
      const icon = btnMic.querySelector('i');
      if (icon) icon.setAttribute('data-lucide', 'square');
    } else {
      btnMic.classList.remove('recording');
      const icon = btnMic.querySelector('i');
      if (icon) icon.setAttribute('data-lucide', 'mic');
      state.liveTranscript = '';
      if (liveText) liveText.textContent = '...';
    }
    if (window.lucide) window.lucide.createIcons();
  }

  if (liveBanner) {
    liveBanner.style.display = isRec ? 'flex' : 'none';
  }
}

// Send user message and query /api/chat
async function handleSendMessage(messageText, container) {
  if (state.isSending) return;

  const userTime = formatTime(new Date());

  // 1. Add User message
  state.messages.push({
    sender: 'user',
    text: messageText,
    data: null,
    time: userTime
  });

  // 2. Add Temporary Thinking Indicator message
  state.isSending = true;
  state.messages.push({
    sender: 'bot',
    text: '...',
    data: null,
    isThinking: true,
    time: formatTime(new Date())
  });

  // Re-render message list
  const msgContainer = container.querySelector('#chat-messages-container');
  if (msgContainer) {
    msgContainer.innerHTML = renderMessagesHtml(state.messages);
    if (window.lucide) window.lucide.createIcons();
    scrollToBottom(container);
  }

  try {
    const lang = getLanguage();
    const res = await api.sendChat(messageText, lang, state.sessionId);

    // Remove thinking message
    state.messages.pop();

    // 3. Add Bot Response message
    const botReply = res.reply || 'Could not process query.';
    state.messages.push({
      sender: 'bot',
      text: botReply,
      intent: res.intent,
      data: res.data,
      time: formatTime(new Date())
    });

    // Re-render
    if (msgContainer) {
      msgContainer.innerHTML = renderMessagesHtml(state.messages);
      if (window.lucide) window.lucide.createIcons();
      scrollToBottom(container);
      bindBubbleEvents(container);
    }

    // 4. Speak response audio (if voice not muted)
    // Always showing the text is preserved above; voice synthesis runs concurrently
    voice.speak(botReply, lang);

  } catch (err) {
    console.error('Chat request error:', err);
    state.messages.pop(); // Remove thinking

    state.messages.push({
      sender: 'bot',
      text: `⚠️ Error contacting advisor service: ${err.message || 'Please check if server is running.'}`,
      data: null,
      time: formatTime(new Date())
    });

    if (msgContainer) {
      msgContainer.innerHTML = renderMessagesHtml(state.messages);
      if (window.lucide) window.lucide.createIcons();
      scrollToBottom(container);
    }
  } finally {
    state.isSending = false;
  }
}

function bindBubbleEvents(container) {
  container.querySelectorAll('.btn-bubble-listen').forEach((btn) => {
    btn.addEventListener('click', () => {
      const rawText = btn.getAttribute('data-text');
      if (rawText) {
        voice.speak(rawText, getLanguage());
      }
    });
  });
}
