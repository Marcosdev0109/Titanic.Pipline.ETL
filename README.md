# 🚢 Titanic Pipeline ETL com IA (Gemini API)

Este projeto implementa um pipeline **ETL (Extract, Transform, Load)** utilizando o clássico dataset do **Titanic**, com uma integração criativa à **API Gemini 2.5 Flash** do Google.  
A proposta é que a IA se passe pela **empresa de marketing da White Star Line** — a companhia responsável por vender as passagens do Titanic —, gerando descrições e campanhas personalizadas para os tripulantes e passageiros.

---

## 🧭 Objetivo

Transformar o dataset histórico em uma experiência interativa e narrativa, unindo **ciência de dados** e **inteligência artificial generativa**.  
A IA analisa os dados de cada passageiro e cria textos promocionais ou campanhas como se fossem feitos pela equipe de marketing antes da fatídica viagem.

---

## ⚙️ Tecnologias Utilizadas

- **Python 3.10+**
- **Pandas** — manipulação e limpeza de dados  
- **Google Gemini API** — geração de conteúdo com IA  
- **Jupyter Notebook / VSCode** — ambiente de desenvolvimento  
- **Requests** — integração com a API  

---

## 🧩 Estrutura do Projeto
Titanic.Pipeline.ETL/
│
├── data/
│ ├── raw/ # Dados originais do Titanic
│ ├── processed/ # Dados limpos e transformados
│
├── notebooks/
│ └── etl_titanic.ipynb # Pipeline principal (extração e transformação)
│
├── src/
│ ├── etl.py # Funções ETL
│ ├── ai_client.py # Integração com a API Gemini
│ └── marketing_prompt.py # Prompt criativo e mensagens
│
├── .env # Contém a chave da API (não versionar)
├── requirements.txt
└── README.md

📈 Futuras Melhorias

Adicionar análise de sentimentos das descrições geradas

Criar visualizações interativas com Streamlit

Implementar uma API REST para consulta em tempo real

Adicionar logs e controle de qualidade das gerações

🧠 Autor

João Marcos
💼 Nutricionista, pesquisador e estudante de Ciência da Computação
📍 Brasil
🔗 LinkedIn

🪙 Licença

Este projeto está sob a licença MIT.
Sinta-se à vontade para usar, estudar e adaptar o código.
