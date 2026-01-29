// 【今日の話題画面】ページ読み込み時の処理
window.onload = function() {
    // 最新コメントまで自動スクロール
    const chatArea = document.getElementById('chat-area');
    if (chatArea) {
        window.scrollTo(0, document.body.scrollHeight);
    }
};

// 【日記を書く画面】保存時の二重送信防止
const diaryForm = document.getElementById('diary-form');
if (diaryForm) {
    diaryForm.onsubmit = function() {
        const btn = document.getElementById('save-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerText = 'AIが返信を考えています...';
        }
    };
}