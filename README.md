初回

リポジトリをクローンする
プロジェクトを保存したいフォルダの階層で、以下のコマンドを打つ
git clone https://github.com/Tech-Jam-KDG-2026-Winter/Team-1-Django.git

プロジェクトの階層に移動する
cd Team-1-Django

仮想環境を作って入る
python3 -m venv venv
source venv/bin/activate

ライブラリのインストール
pip3 install -r requirements.txt

プロジェクトルートに.envファイルを作り、内容を貼り付ける

データベースの準備と起動
python3 manage.py migrate
python3 manage.py runserver
