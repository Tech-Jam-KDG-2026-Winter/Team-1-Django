from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import UserProfile, Diary, DailyThread, ThreadComment
from datetime import timedelta
from django.db.models import Q
from google import genai
from django.conf import settings

User = get_user_model()

# Django標準（django.contrib.auth.urls）を使うのでログイン/ログアウトViewは今回は書きません。

# ユーザー新規登録画面（登録後ログイン画面へ遷移するためログイン不要）
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password_confirm')
        ai_enabled = request.POST.get('ai_enabled') == 'on'

        if User.objects.filter(username=username).exists():
            messages.error(request, "このユーザー名はすでに使われています。")
            return render(request, 'app/user_create.html')
        if pass1 != pass2:
            messages.error(request, "パスワードが一致しません。")
            return render(request, 'app/user_create.html')
        
        try:
            user = User.objects.create_user(username=username, password=pass1)
            UserProfile.objects.create(
                user=user,
                is_advice_enabled=ai_enabled
            )

            messages.success(request, "登録が完了しました！ログインしてください。")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"エラーが発生しました: {e}")
            return render(request, 'app/user_create.html')

    return render(request, 'app/user_create.html')

# メイン機能（ログイン必須）
# テンプレートで今日の日付を表示するために'now'を渡す

# 日記一覧画面（ホーム）
@login_required
def index(request):
    # 1. 前日の日付を取得 (yesterday = timezone.now().date() - timedelta(days=1))
    yesterday = timezone.now().date() - timedelta(days=1)
    # 2. ログインユーザーの日記のうち、「昨日以前（date <= yesterday）」のものを取得。
    # 3. 順序は date降順（昨日のものが1番上）。
    diaries = Diary.objects.filter(
        user = request.user,
        date__lte = yesterday
    ).order_by("-date")

    # 4. 検索フォームの処理（キーワード・期間）はこの「昨日以前」のデータに対して行う。
    q = request.GET.get('q')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    if q:
        # キーワードが本文(content)かAI返信に含まれるか
        diaries = diaries.filter(Q(content__icontains=q) | Q(ai_response__icontains=q))
    if start:
        diaries = diaries.filter(date__gte=start)
    if end:
        diaries = diaries.filter(date__lte=end)
    
    # 5. テンプレートへは取得した日記リストを渡して表示させること。
    context = {
        'diaries': diaries,
        'now': timezone.now()
    }
   
    # - 変数名：日記のリスト名はdiaries
    return render(request, 'app/index.html', context)

# 今日の話題画面
@login_required
def daily_topic(request):
    # 1. DailyThread から今日の日付の「話題」を1件取得（30文字以内）。
    topic = DailyThread.objects.filter(date=timezone.now().date()).first()
 
    # 2. 掲示板コメントを created_at昇順（古いものが上）で全件取得。

    # 3. コメント投稿フォームを画面下部に設置し、投稿時は投稿者と内容を保存。
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text and request.user.is_authenticated:
            # 投稿者(user)と内容(text)を保存
            ThreadComment.objects.create(
                thread = topic,
                user=request.user, 
                content=comment_text
            )
    # 4. ※画面を開いた時に1番下までスクロールさせる処理はJSで書く。
    # 5. コメント投稿時（POST）は、リダイレクト(redirect('daily_topic'))を使って二重投稿を防ぐこと。
        return redirect('daily_topic')

    comments = ThreadComment.objects.filter(created_at__date=timezone.now().date()).order_by('created_at')
    # 6. テンプレートへは「今日のお題」と「コメント一覧」を渡すこと。
    # - 変数名：今日の話題はtopic
    # - 変数名：コメントのリストはcomments
    return render(request, 'app/daily_topic.html', {'topic': topic, 'comments':comments, 'now': timezone.now()})

# 日記を書く（作成・更新）画面
@login_required
def diary_write(request):
    today = timezone.now().date()
    diary = Diary.objects.filter(user=request.user, date=today).first()

    if request.method == 'POST':
        content = request.POST.get('content')
        profile = request.user.userprofile

        diary, created = Diary.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={'content': content}
        )

        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            content_length = len(content)

            if profile.is_advice_enabled:
                if content_length < 150:
                    instruction = "60文字程度で短く温かく共感し、続けて40文字程度で健康維持（食事・睡眠・運動・リフレッシュ）に関する前向きなアドバイスを1つ伝えて。"
                else:
                    target_length = min(int(content_length * 2 / 3), 400)
                    instruction = f"{target_length}文字程度で、内容を深く汲み取って共感した上で、複数の視点から健康維持（食事・睡眠・運動・リフレッシュ）に関する前向きなアドバイスを伝えて。"
            else:
                if content_length < 100:
                    instruction = "60文字程度で、短く温かく共感して。"
                else:
                    target_length = min(int(content_length * 2 / 3), 300)
                    instruction = f"{target_length}文字程度で、日記の内容に深く共感し、丁寧に寄り添って。"

            system_settings = (
                "あなたはユーザーの健康と心を支える専属のカウンセラーです。"
                "常に丁寧で、包み込むような優しさを持った言葉遣いで返信してください。"
                "日記がタメ語であっても敬語であっても、一貫して「です・ます」調の丁寧な言葉を使い、安心感を提供してください。"
                "【内容のガイドライン】"
                "・事務的な敬語ではなく、親身になって寄り添う柔らかい表現を選んでください。"
                "・数日後に読み返しても役立つよう、「今すぐ」「今夜は」などは使わず、「疲れた時は」「次に〜する時は」といった持続的な表現にしてください。"
                "・【】や「---」、箇条書きは使わず、自然なメッセージのみで構成してください。"
            )
            
            prompt = f"{system_settings}\n\n指示：{instruction}\n\n日記内容：\n{content}"
            
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=prompt
            )
            
            diary.ai_response = response.text
            diary.save()

        except Exception as e:
            diary.ai_response = f"エラーが発生しました: {e}"
            diary.save()

        return redirect('index')

    return render(request, 'app/diary_write.html', {'now': timezone.now(), 'diary': diary})

# 日記詳細
class DiaryDetailView(LoginRequiredMixin, DetailView):
    model = Diary
    template_name = 'app/diary_detail.html'
    context_object_name = 'diary'

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

# 設定画面
class SettingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    template_name = 'app/setting.html'
    fields = ['is_advice_enabled']         # ← クラス属性
    context_object_name = 'profile'       # ← クラス属性
    success_url = reverse_lazy('setting') # ← クラス属性
    success_message = "設定を更新しました."

    def get_object(self):
        return self.request.user.userprofile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()    # ← 関数内で now をセット
        return context
