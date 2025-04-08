mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = false
address = \"0.0.0.0\"

[theme]
primaryColor = \"#F63366\"
backgroundColor = \"#FFFFFF\"
secondaryBackgroundColor = \"#F0F2F6\"
textColor = \"#262730\"
font = \"sans serif\"
" > ~/.streamlit/config.toml