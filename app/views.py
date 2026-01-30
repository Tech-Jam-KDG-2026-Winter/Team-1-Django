from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import UserProfile, Diary, DailyThread, ThreadComment
from google import genai
from django.conf import settings

# Django標準（django.contrib.auth.urls）を使うのでログイン/ログアウトViewは今回は書きません。

# ユーザー新規登録画面（ログイン不要）
def user_create(request):
    # 1. フォームから「ユーザー名」「パスワード」「確認用パスワード」を取得。
    # 2. パスワードが一致するか確認。
    # 3. User.objects.create_user() で auth_user に保存。
    # 4. 同時に UserProfile.objects.create(user=user) でプロフィールも作成。
    # 5. 保存後、ログイン画面へ遷移させる。
    # - 「すでにこのユーザー名は使われています」というエラーを画面に出す(unique制約があるため)
    # - auth_user に保存する際は、パスワードをハッシュ化（暗号化）して保存してくれる User.objects.create_user() を使う
    # - 変数名：エラーメッセージはmessages（django.contrib.messages を使用）
    return render(request, 'app/user_create.html')

# メイン機能（ログイン必須）
# テンプレートで今日の日付を表示するために'now'を渡す

# 日記一覧画面（ホーム）
@login_required
def index(request):
    # 1. 前日の日付を取得 (yesterday = timezone.now().date() - timedelta(days=1))
    # 2. ログインユーザーの日記のうち、「昨日以前（date <= yesterday）」のものを取得。
    # 3. 順序は date降順（昨日のものが1番上）。
    # 4. 検索フォームの処理（キーワード・期間）はこの「昨日以前」のデータに対して行う。
    # 5. テンプレートへは取得した日記リストを渡して表示させること。
    # - 変数名：日記のリスト名はdiaries
    return render(request, 'app/index.html', {'now': timezone.now()})

# 今日の話題画面
@login_required
def daily_topic(request):
    # 1. DailyThread から今日の日付の「話題」を1件取得（30文字以内）。
    # 2. 掲示板コメントを created_at昇順（古いものが上）で全件取得。
    # 3. コメント投稿フォームを画面下部に設置し、投稿時は投稿者と内容を保存。
    # 4. ※画面を開いた時に1番下までスクロールさせる処理はJSで書く。
    # 5. コメント投稿時（POST）は、リダイレクト(redirect('daily_topic'))を使って二重投稿を防ぐこと。
    # 6. テンプレートへは「今日のお題」と「コメント一覧」を渡すこと。
    # - 変数名：今日の話題はtopic
    # - 変数名：コメントのリストはcomments
    return render(request, 'app/daily_topic.html', {'now': timezone.now()})

# 日記を書く（作成・更新）画面
@login_required
def diary_write(request):

    return render(request, 'app/diary_write.html', {'now': timezone.now()})

# 日記詳細
class DiaryDetailView(LoginRequiredMixin, DetailView):
    # 1. model = Diary, template_name = 'app/diary_detail.html' を指定。
    # 2. get_queryset をオーバーライドし、自分の日記のみ取得可能にする（セキュリティ）。
    # 3. get_context_data でテンプレートに 'now': timezone.now() を追加で渡す。
    # 4. context_object_name = 'diary'を設定する（htmlに合わせる）(変数名：日記詳細データはdiary)
    pass # このpassは消して、ロジックを書いていってください。

# 設定画面
class SettingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    # 1. model = UserProfile, template_name = 'app/setting.html' を指定。
    # 2. fields = ['ai_enabled'] を指定して、トグルボタンの値だけを更新対象にする。
    # 3. get_object をオーバーライドし、URLのpkではなく「self.request.user.userprofile」を返す。
    # 4. get_context_data でテンプレートに 'now': timezone.now() を追加で渡す。
    # 5. context_object_name = 'profile' を設定する（htmlの変数名に合わせる）。
    # 6. success_url = reverse_lazy('setting') で更新後に自分自身へリダイレクトさせる。
    pass # このpassは消して、ロジックを書いていってください。