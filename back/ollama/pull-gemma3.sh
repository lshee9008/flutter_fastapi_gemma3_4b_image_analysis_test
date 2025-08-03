bin/ollama serve &

pid=&!

sleep 5

echo "Pulling gemma3:4b model"
ollama pull gemma3:4b


wait $pid