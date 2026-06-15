import os
import asyncio
import httpx
import pytz
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
 
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
FUSO = pytz.timezone("America/Sao_Paulo")
 
async def chamar_claude(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-6", "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]}
        )
        data = r.json()
        return data["content"][0]["text"]
 
async def enviar(bot: Bot, msg: str):
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
 
async def resumo_matinal(bot: Bot):
    msg = await chamar_claude("""Você é assistente pessoal de uma biomédica brasileira, tricologista, especialista em harmonização facial e skincare, com 63k seguidores no Instagram.
 
Crie um resumo matinal COMPLETO para hoje com exatamente estas seções:
 
🌍 *MUNDO HOJE*
3 notícias reais e relevantes do mundo (geopolítica, economia, Copa do Mundo se estiver acontecendo, EUA, Europa)
 
💆 *BELEZA & ESTÉTICA*
2 novidades científicas ou tendências da área de dermatologia, tricologia, harmonização facial ou skincare
 
💼 *EMPREENDEDORISMO*
1 dica ou tendência de marketing digital / Instagram / criação de conteúdo
 
🌱 *FRASE DO DIA*
Uma frase motivacional poderosa e real (com autor)
 
Seja direta, informativa e use linguagem acessível. Máximo 300 palavras no total.""")
    await enviar(bot, f"☀️ *BOM DIA! Seu resumo de hoje:*\n\n{msg}")
 
async def ideia_conteudo(bot: Bot):
    msg = await chamar_claude("""Sugira UMA ideia de conteúdo para Instagram/TikTok para uma biomédica e tricologista brasileira especializada em skincare, harmonização facial e cuidados capilares.
 
Formato:
📸 *CONTEÚDO DO DIA*
*Tipo:* (Reels / Carrossel)
*Título:* ...
*Hook:* (primeira frase que prende em até 3 segundos)
*Roteiro rápido:* (3 pontos, vídeo até 1 minuto)
*Legenda sugerida:* (com emojis e hashtags)""")
    await enviar(bot, msg)
 
async def noticia_tarde(bot: Bot):
    msg = await chamar_claude("Dê um update rápido de 2 notícias importantes que aconteceram hoje no mundo. Seja direta e real. Use emojis. Máximo 100 palavras.")
    await enviar(bot, f"📰 *Update da tarde:*\n\n{msg}")
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌸 *Olá Fernanda! Sou sua assistente pessoal!*\n\nUse /id para pegar seu Chat ID!", parse_mode="Markdown")
 
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Seu Chat ID é: `{chat_id}`", parse_mode="Markdown")
 
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
 
    s = AsyncIOScheduler(timezone=FUSO)
    b = app.bot
 
    # TODOS OS DIAS
    s.add_job(resumo_matinal, "cron", day_of_week="mon-sun", hour=7, minute=0, args=[b])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=7, minute=10, args=[b, "📝 *Intenção do dia:* Escreve 1 objetivo antes de abrir qualquer rede social. ✨"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=7, minute=15, args=[b, "✍️ *Diário matinal:* 5-10 minutos escrevendo o que está sentindo. Sem julgamento. 🌸"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=6, minute=55, args=[b, "💊 *REMÉDIOS antes da academia:*\n✅ Finalope 1mg\n✅ Espironolactona 50mg\n✅ Minoxidil oral 1mg\n✅ Supercof 1 scoop\n✅ Cappuccino Zero 1 scoop"])
    s.add_job(enviar, "cron", day_of_week="mon,fri", hour=7, minute=0, args=[b, "💊 *ROAKI — tomar hoje!* (segunda e sexta) 🌟"])
    s.add_job(enviar, "cron", day_of_week="wed,sun", hour=21, minute=0, args=[b, "💊 *Metronidazol intravaginal — aplicar hoje!* (quarta e domingo) 🌸"])
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=8, minute=0, args=[b, "🏋️ *ACADEMIA — AGORA!* Das 8h às 9h. 💪"])
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=8, minute=5, args=[b, "📱 *Você está na esteira?* Abre o WhatsApp e responde por *10 minutos*. Timer já! ⏱️"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=9, minute=30, args=[b, "💧 *Água #1 de 3L* — 500ml agora! 🫙"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=9, minute=45, args=[b, "📊 *CHECK Instagram:* Quantos seguidores hoje?\n🎯 Meta junho: *64.000* | Meta 2026: *100.000*"])
    s.add_job(ideia_conteudo, "cron", day_of_week="mon-fri", hour=10, minute=0, args=[b])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=12, minute=0, args=[b, "💧 *Água #2 de 3L* — 500ml antes do almoço! 🫙"])
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=12, minute=30, args=[b, "📱 *Instagram — 15 min de engajamento.* Timer ANTES de abrir! ⏱️"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=14, minute=0, args=[b, "🍎 *Frutas do dia!* Já comeu suas 2-3 frutas? 🍌🍓"])
 
    # ANTI-CIGARRO
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=16, minute=45, args=[b, "🚨 *ALERTA — 17h chegando!* Horário de risco!\n\n💡 Escolhe uma:\n• Liga pro Luigi\n• Chá gelado\n• 20 agachamentos\n• Skincare\n• 1 música favorita\n\nA vontade passa em 3 minutos! 💪"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=17, minute=0, args=[b, "🚭 *SÃO 17H — NÃO ACENDE!*\nInspira 4s, segura 4s, expira 4s. Repete 5x agora. 🫁"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=17, minute=30, args=[b, "💪 *30 min sem fumar!* PARABÉNS! Bebe água com gás. 🥂"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=18, minute=0, args=[b, "🌅 *1 hora livre do cigarro!* Seu colágeno agradece! 🌸"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=19, minute=0, args=[b, "🍵 *Ritual noturno saudável:*\n1. Skincare\n2. Série ou música\n3. Chá relaxante\n4. Conversa com Luigi 💛"])
 
    # NOITE
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=20, minute=0, args=[b, "💧 *Água #3 — reta final dos 3L!* 🫙"])
    s.add_job(noticia_tarde, "cron", day_of_week="mon-sun", hour=20, minute=30, args=[b])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=21, minute=0, args=[b, "✅ *Revisão do dia:*\n1️⃣ O que fiz que me orgulho?\n2️⃣ O que deixei pra amanhã?\n3️⃣ Fumei hoje? 🌙"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=21, minute=30, args=[b, "📵 *MODO NOTURNO!* Celular de lado. Boa noite! 🌙✨"])
 
    # SEGUNDA
    s.add_job(enviar, "cron", day_of_week="mon", hour=10, minute=50, args=[b, "🧠 *Terapia em 10 min!* Leva a tarefa da terapeuta! 💬"])
    s.add_job(enviar, "cron", day_of_week="mon", hour=13, minute=0, args=[b, "📚 *TAREFA DA TERAPIA — faz AGORA!* 50 min antes do inglês. Timer! ⏱️"])
    s.add_job(enviar, "cron", day_of_week="mon", hour=13, minute=50, args=[b, "🌍 *Inglês em 10 min!* (14h-15h) Your future self will thank you! 💪"])
    s.add_job(enviar, "cron", day_of_week="mon", hour=15, minute=30, args=[b, "📝 *Tarefa de inglês — faz AGORA!* Enquanto está fresco! 20 min. ⏱️"])
 
    # TERÇA/QUARTA/QUINTA
    s.add_job(enviar, "cron", day_of_week="tue,wed,thu", hour=10, minute=30, args=[b, "📖 *Ebook — 20 minutos AGORA!* Escreve sem editar. ✍️"])
    s.add_job(enviar, "cron", day_of_week="tue,wed,thu", hour=12, minute=45, args=[b, "👩‍⚕️ *Consultório em 15 min!* Vai arrasar! ✨"])
 
    # QUINTA
    s.add_job(enviar, "cron", day_of_week="thu", hour=6, minute=50, args=[b, "🚴 *Spinning em 10 min!* (7h-8h) 💪"])
    s.add_job(enviar, "cron", day_of_week="thu", hour=9, minute=15, args=[b, "🇫🇷 *Duolingo francês!* 5-10 min agora. Bonjour! 🥐"])
 
    # LAVANDERIA
    s.add_job(enviar, "cron", day_of_week="mon,wed,fri", hour=9, minute=0, args=[b, "🧺 *Lavar roupas hoje!* Coloca a máquina antes de trabalhar. 💪"])
    s.add_job(enviar, "cron", day_of_week="wed", hour=9, minute=5, args=[b, "🛏️ *Quarta = roupas de cama também!* Troca o lençol! 😄"])
 
    # INSTAGRAM
    s.add_job(enviar, "cron", day_of_week="tue", hour=10, minute=15, args=[b, "🎓 *TERÇA = CONTEÚDO EDUCATIVO!* Hook forte nos primeiros 3s! Vídeo até 1 min. 🎬"])
    s.add_job(enviar, "cron", day_of_week="thu", hour=10, minute=15, args=[b, "🤝 *QUINTA = PARCERIA OU PROCEDIMENTO!* Não esquece collab e cupom! ✅"])
    s.add_job(enviar, "cron", day_of_week="sat", hour=10, minute=15, args=[b, "🌸 *SÁBADO = LIFESTYLE!* Conteúdo leve que fideliza. Mostra você como pessoa! 💛"])
    s.add_job(enviar, "cron", day_of_week="fri", hour=20, minute=0, args=[b, "📈 *ANÁLISE DA SEMANA:*\n1️⃣ Quantos posts?\n2️⃣ Qual teve mais views?\n3️⃣ Ganhou seguidores?\n\nManda prints pro Claude! 🚀"])
    s.add_job(enviar, "cron", day_of_week="sun", hour=9, minute=0, args=[b, "📋 *Domingo — planeja a semana!*\n✅ Que conteúdos vou criar?\n✅ Tenho tarefas pendentes?\n\nQuem planeja no domingo não procrastina na segunda! 💡"])
    s.add_job(enviar, "cron", day_of_week="sat", hour=9, minute=0, args=[b, "🌸 *Sábado — dia de recarregar!* Faz algo que te dá prazer. E bebe os 3L! 😄✨"])
 
    s.start()
    print("✅ Bot rodando!")
 
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()
 
if __name__ == "__main__":
    asyncio.run(main())
 
