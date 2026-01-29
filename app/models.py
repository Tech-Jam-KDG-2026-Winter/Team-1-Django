from django.db import models
from django.contrib.auth.models import User

# ユーザーのAIスタンス設定
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # True: 褒める＋アドバイス / False: 褒めるだけ
    is_advice_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

# 日記とAIの返信（1日1通、0時確定）
class Diary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.date} - {self.user.username}"

# 管理者が事前に登録する今日のお題
class DailyThread(models.Model):
    # 保存エラー防止のため100文字に拡張（運用上は30文字程度を推奨）
    title = models.CharField(max_length=100)
    date = models.DateField(unique=True)

    def __str__(self):
        return f"{self.date}: {self.title}"

# お題スレッドへのみんなの書き込み
class ThreadComment(models.Model):
    thread = models.ForeignKey(DailyThread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
