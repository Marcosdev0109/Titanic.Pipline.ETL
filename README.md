# Bilhete para o Titanic

Pipeline ETL em Python com os 891 passageiros reais do Titanic e um site onde você escolhe um passageiro, lê o anúncio que a IA escreveu para ele e vira o bilhete para descobrir o destino.

**Demo:** https://marcosdev0109.github.io/Titanic.Pipline.ETL/

## O que o projeto faz

| Etapa | Onde | O que acontece |
|---|---|---|
| Extract | `pipeline/etl.py` | Lê `dados/titanic.csv` (891 passageiros, 12 colunas) |
| Transform | `pipeline/etl.py` | Tira o título do nome (Sr., Sra., Srta., Menino), estima as 177 idades faltando pela mediana do título, completa os 2 portos vazios, calcula família a bordo, convés e faixa etária |
| IA | `pipeline/etl.py --ia N` | O Gemini escreve, como a equipe de marketing da White Star Line em 1912, um anúncio personalizado para N passageiros. O prompt não recebe o destino do passageiro |
| Load | `docs/data/*.json` | Salva passageiros, estatísticas de sobrevivência e anúncios |
| Site | `docs/index.html` | HTML, CSS e JavaScript puros: busca sem acento, filtros, bilhete que vira e gráficos |

## O que os dados mostram

- 38% dos passageiros sobreviveram (342 de 891).
- Primeira classe: 63%. Terceira classe: 24%.
- Mulheres: 74%. Homens: 19%.
- Crianças até 12 anos: 57%.

## Como rodar

```bash
pip install -r requirements.txt
python pipeline/etl.py                    # ETL sem IA
export GOOGLE_API_KEY="sua_chave"         # a chave fica fora do código
python pipeline/etl.py --ia 20            # gera 20 anúncios novos com o Gemini
python -m http.server -d docs             # abre o site em http://localhost:8000
```

Os 12 anúncios da demonstração foram escritos por IA a partir dos dados de cada passageiro. São ficção, não registro histórico.

## Segurança

A versão anterior deste repositório tinha uma chave de API escrita no notebook. Ela foi retirada do código e precisa ser revogada no Google AI Studio, porque continua no histórico do Git. O código novo lê a chave da variável de ambiente `GOOGLE_API_KEY`.

## Tecnologias

Python, Pandas, Google Gemini API, HTML, CSS e JavaScript, GitHub Pages.

## Autor

João Marcos Rodrigues Barbosa · [Portfólio](https://marcosdev0109.github.io) · [LinkedIn](https://www.linkedin.com/in/joao-marcos01)
