:moneybag: Dashboard de Investimentos



Dashboard pessoal para acompanhamento e análise de investimentos.



:rocket: Como usar



Rodar o dashboard
Adiciona novos aportes/resgates do mês
Adiciona saldo atualizado de cada investimento (última linha de cada mês)
cd ~/Documents/investments_tracker
streamlit run dashboard.py
~~~

O dashboard abre automaticamente no navegador.

Para fechar: apertar `Ctrl+C` no terminal.

*📝 Como atualizar mensalmente*

*Passo 1:* Atualiza a planilha do Google Sheets

*Passo 2:* Sincroniza os dados
cd ~/Documents/investments_tracker
python sync_google_sheets.py
*Passo 3:* Abre o dashboard
streamlit run dashboard.py
Patrimônio total e rendimento acumulado
Distribuição por tipo de investimento e risco
Evolução mensal do patrimônio (desde Fev/2026)
Rentabilidade acumulada com filtros por produto/risco
Planilha: https://docs.google.com/spreadsheets/d/1ZnW3wgE5XIamWv3vC22ybnQ3cmzXec9cIxsOP0mfH28
Repositório: https://github.com/mandsnunes/investments-dashboard

Pronto! 🎉

*📊 O que o dashboard mostra*


*🔗 Links*


-------------------------
Criado em Fevereiro de 2026
