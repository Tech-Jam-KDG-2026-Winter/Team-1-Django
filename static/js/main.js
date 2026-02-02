// 【DailyTopic画面】ページ読み込み時の処理
window.onload = function() {
    // 最新コメントまで自動スクロール
    const chatArea = document.getElementById('chat-area');
    if (chatArea) {
        window.scrollTo(0, document.body.scrollHeight);
    }
};

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