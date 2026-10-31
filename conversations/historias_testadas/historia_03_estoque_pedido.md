# História 3 — Preço, estoque e pedido

- Status do teste: Concluído
- Provedor: Groq (`openai/gpt-oss-20b`)
- Execução: 2026-10-31 18:42:07 -0300

## Conversa

**Cliente:** Quanto custa o Takamine GD20?

**Atendente:** O Takamine GD20 Dreadnought Natural sai por **R$ 2.199,00**.  
Ele está em estoque (5 unidades disponíveis) e pronto para envio. Se quiser fazer o pedido ou precisar de mais detalhes, é só falar!

**Cliente:** Tem dele a pronta entrega na loja de Campo Grande ou precisa encomendar?

**Atendente:** Sim! O Takamine GD20 Dreadnought Natural está **pronta entrega** na nossa loja de Campo Grande – temos 5 unidades em estoque.  
Se quiser garantir o seu, é só passar aqui ou fazer o pedido online e a gente já prepara para você. 🎸

**Cliente:** Legal! Mas já aproveitando, fiz uma compra semana passada de outro produto. Como faço para ver o status do meu pedido?

**Atendente:** Para eu conseguir te ajudar com o status do seu pedido, preciso saber o número do pedido (order ID). Pode me passar esse número? Assim eu verifico tudo pra você!

**Cliente:** O pedido é o #1042 em nome de Carlos Eduardo.

**Atendente:** Desculpe, não encontrei nenhum pedido com o número **1042** nos nossos registros.  
Você poderia confirmar se o número está correto ou me passar algum outro detalhe (por exemplo, data de compra ou e‑mail usado)? Assim consigo localizar o seu pedido e te informar o status.

## Ferramentas acionadas por pergunta

- Pergunta 1: `search_products`
- Pergunta 2: `check_stock`
- Pergunta 3: nenhuma ferramenta
- Pergunta 4: `get_order_status`
