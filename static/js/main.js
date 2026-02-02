// 【DailyTopic画面】ページ読み込み時の処理
document.addEventListener("DOMContentLoaded", function() {
    const chatArea = document.getElementById('chat-area');
    if (!chatArea) return;

    const today = new Date().toLocaleDateString(); 
    const storageKey = 'topic_scroll_pos_' + today;
    const isSubmitted = document.referrer.includes(window.location.pathname);

    // 1. スクロール位置の復元
    if (isSubmitted) {
        // 自分のコメント送信後は一番下へ
        chatArea.scrollTop = chatArea.scrollHeight;
    } else {
        // 保存された位置があればそこへ、なければ何もしない（初回なら上端）
        const savedPos = localStorage.getItem(storageKey);
        if (savedPos) {
            chatArea.scrollTop = parseInt(savedPos, 10);
        }
    }

    // 2. スクロールするたびに位置を保存する
    chatArea.addEventListener('scroll', function() {
        localStorage.setItem(storageKey, chatArea.scrollTop);
        
        // 前日の古いデータは消しておく（メモリ節約）
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('topic_scroll_pos_') && key !== storageKey) {
                localStorage.removeItem(key);
            }
        }
    });
});

// 【WriteDiary画面】保存時の二重送信防止
const diaryForm = document.getElementById('diary-form');
if (diaryForm) {
    diaryForm.onsubmit = function() {
        const btn = document.getElementById('save-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerText = '保存しています...';
        }
    };
}