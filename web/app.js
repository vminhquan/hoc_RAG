// Giao diện hỏi đáp: gửi câu hỏi lên POST /api/chat và hiển thị câu trả lời của chatbot.

const API_URL = "/api/chat";
const REQUEST_TIMEOUT_MS = 90000; // LLM timeout là 60s, chờ dư thêm cho retriever + mạng

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("question");
const sendEl = document.getElementById("send");
const suggestionsEl = document.getElementById("suggestions");

// Thêm 1 tin nhắn vào khung chat.
// Dùng textContent (không dùng innerHTML) để nội dung từ user/LLM không thể chèn mã HTML/JS độc hại (XSS).
function addMessage(text, role) {
  const messageEl = document.createElement("div");
  messageEl.className = `message message--${role}`;

  const bubbleEl = document.createElement("div");
  bubbleEl.className = "message__bubble";
  bubbleEl.textContent = text;

  messageEl.appendChild(bubbleEl);
  messagesEl.appendChild(messageEl);
  scrollToBottom();
  return messageEl;
}

// Hiện hiệu ứng 3 chấm "đang trả lời..." trong lúc chờ server
function addTypingIndicator() {
  const messageEl = document.createElement("div");
  messageEl.className = "message message--bot";
  messageEl.innerHTML = '<div class="message__bubble"><span class="typing" aria-label="Đang trả lời"><span></span><span></span><span></span></span></div>';
  messagesEl.appendChild(messageEl);
  scrollToBottom();
  return messageEl;
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Khóa/mở ô nhập để user không gửi nhiều câu hỏi cùng lúc
function setLoading(isLoading) {
  inputEl.disabled = isLoading;
  sendEl.disabled = isLoading;
  if (!isLoading) inputEl.focus();
}

// Gọi API backend, trả về câu trả lời dạng string
async function fetchAnswer(question) {
  // AbortController: tự hủy request nếu server không phản hồi quá lâu
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.answer;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Luồng chính khi user gửi câu hỏi
async function sendQuestion(question) {
  question = question.trim();
  if (!question) return;

  // Ẩn câu hỏi gợi ý sau lần hỏi đầu tiên cho gọn giao diện
  suggestionsEl.hidden = true;

  addMessage(question, "user");
  inputEl.value = "";
  autoResize();
  setLoading(true);

  const typingEl = addTypingIndicator();

  try {
    const answer = await fetchAnswer(question);
    typingEl.remove();
    addMessage(answer, "bot");
  } catch (error) {
    typingEl.remove();
    console.error("Chat request failed:", error);

    const message = error.name === "AbortError"
      ? "Server phản hồi quá lâu, bạn thử hỏi lại nha! 🙏"
      : "Không kết nối được tới server, bạn kiểm tra lại mạng hoặc thử lại sau nha! 🙏";
    addMessage(message, "bot message--error");
  } finally {
    setLoading(false);
  }
}

// Ô nhập tự giãn chiều cao theo nội dung (tối đa theo max-height trong CSS)
function autoResize() {
  inputEl.style.height = "auto";
  inputEl.style.height = `${inputEl.scrollHeight}px`;
}

// ===== Gắn sự kiện =====

// Bấm nút gửi
formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  sendQuestion(inputEl.value);
});

// Enter để gửi, Shift + Enter để xuống dòng
// isComposing: bỏ qua Enter khi đang gõ dấu tiếng Việt bằng bộ gõ (Unikey, EVKey...)
inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

inputEl.addEventListener("input", autoResize);

// Bấm câu hỏi gợi ý -> gửi luôn
suggestionsEl.addEventListener("click", (event) => {
  const button = event.target.closest(".suggestion");
  if (button) sendQuestion(button.textContent);
});

inputEl.focus();
