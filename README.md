<<<<<<< HEAD

=======
>>>>>>> ceb0e3e88ec2e59c8918f7ff7a9b32ffe038ed4b
## 安裝

1. 去kafka下載kafka_2.12-2.4.1.tgz並解壓縮到User的目錄下(跟桌面同層級，不然會出現命令過長的錯誤)
2. 切換目錄並開啟zookeeper
```
cd .\kafka_2.12-2.4.1\
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```
3. 開啟kafka server
```
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

4. 建立topic(該專案有多個topic，這邊只展示login_events)，需要自己補充其他topic
```
.\bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic login_events
```
5. 建立接收特定topic訊息的consumer
```
.\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic login_events --from-beginning
```

6. 使用```pip install -r requirements.txt```安裝所需套件

7. 開啟app.py會跳出頁面，進行登入操作，該server會成為producer發送訊息到特定topic
