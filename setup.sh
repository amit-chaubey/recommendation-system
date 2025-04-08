mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = true
address = \"0.0.0.0\"

[browser]
serverAddress = \"0.0.0.0\"
serverPort = $PORT

[theme]
primaryColor = \"#F63366\"
backgroundColor = \"#FFFFFF\"
secondaryBackgroundColor = \"#F0F2F6\"
textColor = \"#262730\"
font = \"sans serif\"
" > ~/.streamlit/config.toml