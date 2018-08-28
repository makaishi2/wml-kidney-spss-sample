# 慢性腎疾患判定モデル サンプルアプリ

## アプリケーションの説明
このアプリケーションは**Watson Studio**の**SPSS Modeler**で作った慢性腎疾患モデルにWebサービス経由でアクセスし、該当データの持ち主が慢性腎疾患にかかっているかどうかを判定します。

![](readme_images/kidney-web1.png)  

## 前提
Watson Studio上で、慢性腎疾患判定モデルの構築、学習、保存、WEBサービス化、テストまでできていることが前提です。  
詳細手順に関しては、[SPSSクラウド版で簡単機械学習](https://qiita.com/makaishi2/items/85d7694168e71ee3c094)を参照して下さい。

## ibmcloudコマンドの導入
導入にはibmcloudコマンドを利用します。  
ibmcloudコマンドが未導入の場合は、以下のリンク先からダウンロード・導入を行って下さい。  
[IBM Cloudコマンドラインツール](https://console.bluemix.net/docs/cli/reference/ibmcloud/download_cli.html#install_use)  
注意: ibmcloudコマンドのバージョンは最新として下さい。 

## ソースのダウンロード
Githubからアプリケーションのソースをダウンロードします。  
カレントディレクトリのサブディレクトリにソースはダウンロードされるので、あらかじめ適当なサブディレクトリを作り、そこにcdしてから下記のコマンドを実行します。  
GITコマンドを使わない場合は、[Github](## ソースのダウンロード
Githubからアプリケーションのソースをダウンロードします。  
カレントディレクトリのサブディレクトリにソースはダウンロードされるので、あらかじめ適当なサブディレクトリを作り、そこにcdしてから下記のコマンドを実行します。  
GITコマンドを使わない場合は、[Github](https://github.com/makaishi2/wml-kidney-spss-sample) にブラウザからアクセスして、zipファイルをダウンロード後、解凍します。  
ダウンロード後、できたサブディレクトリにcdします。  
以下はgitコマンドを使う場合の例です。


```sh
$ cd (適当なサブディレクトリ)
$ git clone https://github.com/makaishi2/wml-kidney-spss-sample.git
$ cd wml-kidney-sample
```

## ibmcloudコマンドでログイン
IBM Cloud環境にログインします。  
ログイン名、パスワードはIBM Cloudアカウント登録で登録したものを利用します。  
ログイン後には、``ibmcloud target --cf``コマンドを実行し、ターゲットの組織とスペースを確定して下さい。

```
$ ibmcloud login
$ ibmcloud target --cf
```

## Watson MLサービス名称の確認
次のコマンドを実行し、Watson MLのサービス名称(サービス名がpm-20のもの)を確認します。

```
$ ibmcloud service list
```

もし、Watson MLのサービス名がない場合は、Watson Machine LearningがIAMサービスになっていると考えられます。
その場合は、以下の手順でエイリアス定義を行って下さい。

```
# Machine Learningのインスタンス名確認
$ ibmcloud resource service-instances

# エイリアス定義
$ ibmcloud resource service-alias-create machine-learning-1 --instance-name "Machine Learning-xx"

# エイリアス"machine-learning-1" が登録されたことの確認
$ ibmcloud service list
```

以下では、Watson MLサービス名を``machine-learning-1``であるとします。


## アプリケーションのデプロイ

次のコマンドを実行します。
**\<APP_NAME\>** はなんでもいいのですが、インターネット上のURLの一部となるので、ユニークな名前を指定します。  
(例) **wml-kidney-spss-aka7**

```
$ ibmcloud app push <service_name>
```

## サービスのバインド・環境変数の設定

次のcfコマンドでサービスのバインドとエンドポイントURLの設定を行います。
scoring_urlは、Watson StudioのWebサービス管理画面->Implementationタブの**Scoreing End-point**の欄に記載があるので、コピペして利用します。
コマンドのうちrestageコマンド(アプリケーションの再構築)に数分の時間がかかります。

```
# Machine Learning サービスのバインド
$ ibmcloud service bind <APP_NAME> machine-learning-1

# SCORING_URLの設定
$ ibmcloud app env-set <APP_NAME> SCORING_URL <scoring_url>

# アプリケーションの再構成 (設定変更の有効化)
$ ibmcloud app restage <APP_NAME>

# アプリケーションのURLを確認
$ ibmcloud app list
```

## アプリケーションのURLと起動

デプロイが正常に完了したらアプリケーションを起動できます。  
最後のコマンド出力からアプリケーションのURLを調べて、そのURLをブラウザから入力して下さい。URLは通常下記の形になっています。

```
https://<service_name>.mybluemix.net/
```


## アプリケーションを修正する場合

アプリケーションを修正したい場合は、ローカルのソースを修正し、再度 ``ibmcloud app push <service_name>`` コマンドを実行すると、IBM Cloud上のアプリケーションが更新されます。  

## ローカルで起動する場合

アプリケーションを修正する時は、ローカルでもテストできる方が便利です。そのための手順は以下の通りです。

* Pythonの導入  
ローカルにPython(v3)を導入する必要があります。　MACの場合は最初から導入済みなのでこの手順は不要です。
* 認証情報の確認  
BluemixダッシュボードからWMLサービスの管理画面を開き、接続用の認証情報を調べてテキストエディタなどにコピーします。
* .envファイルの設定  
次のコマンドで.env.exampleファイルの雛形から.envをコピーし、エディタで調べたusername, passwordを設定します。

```sh
$ cp .env.example .env
```

```sh
WML_URL="xxxxxx"
WML_ACCESS_KEY="xxxxxx"
WML_USERNAME="xxxxxx"
WML_PASSWORD="xxxxxx"
WML_INSTANCE_ID="xxxxxx"
SCORING_URL="xxxxxx"
```

* Pythonアプリケーションの導入、実行  
以下のコマンドでアプリケーションの導入、実行を行います。

```sh
$ python server.py
```
