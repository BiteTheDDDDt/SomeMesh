docker stop $(docker ps -a | grep "test-optimizer" | awk '{print $1 }')
docker rm $(docker ps -a | grep "test-optimizer" | awk '{print $1 }')

echo "clear previous image"

docker build -t test-optimizer .
docker run -p 8000:3001 -d test-optimizer

echo "build and run new image"

docker cp sample/accesslog-2.txt $(docker ps -a | grep "test-optimizer" | awk '{print $1 }'):/app/accesslog.txt

echo "cp log file"
sleep 1
python3 test.py

echo "run test"