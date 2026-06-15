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
    msg = await chamar_claude("""Você é assistente pessoal de uma biomédica brasileira, tricologista, especialista em harmonização facial e skincare, com 63k seguidores no Instagram. Ela também está aprendendo inglês e francês.

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

Formato da resposta:
📸 *CONTEÚDO DO DIA*
*Tipo:* (Reels / Carrossel)
*Título:* ...
*Hook:* (primeira frase que prende atenção em até 3 segundos)
*Roteiro rápido:* (3 pontos do que falar, vídeo até 1 minuto)
*Legenda sugerida:* (com emojis e hashtags do nicho)

Seja criativa, atual e baseada em tendências reais de 2026.""")
    await enviar(bot, msg)

async def noticia_tarde(bot: Bot):
    msg = await chamar_claude("""Dê um update rápido de 2 notícias importantes que aconteceram hoje no mundo. Seja direta e real. Use emojis. Máximo 100 palavras.""")
    await enviar(bot, f"📰 *Update da tarde:*\n\n{msg}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌸 *Olá Fernanda! Sou sua assistente pessoal!*\n\nUse /id para pegar seu Chat ID e ativar os lembretes.",
        parse_mode="Markdown"
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Seu Chat ID é: `{chat_id}`\n\nManda esse número para ativar seus lembretes!", parse_mode="Markdown")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))

    s = AsyncIOScheduler(timezone=FUSO)
    b = app.bot

    # TODOS OS DIAS
    s.add_job(resumo_matinal, "cron", day_of_week="mon-sun", hour=7, minute=0, args=[b])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=7, minute=10, args=[b, "📝 *Intenção do dia:* Antes de abrir qualquer rede social — escreve no papel 1 objetivo pra hoje. ✨"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=7, minute=15, args=[b, "✍️ *Diário matinal:* Escreve por 5-10 minutos o que está sentindo. Sem julgamento, só escreve. 🌸"])
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=8, minute=0, args=[b, "🏋️ *ACADEMIA — AGORA!* Das 8h às 9h. Pré-treino tomado, sem desculpa! 💪"])
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=8, minute=5, args=[b, "📱 *Você está na esteira?* Abre o WhatsApp AGORA e responde as mensagens por *10 minutos*. Timer já! ⏱️"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=9, minute=30, args=[b, "💧 *Água #1 de 3L* — Já bebeu 500ml hoje? Pega a garrafinha agora! 🫙"])
    s.add_job(ideia_conteudo, "cron", day_of_week="mon-fri", hour=10, minute=0, args=[b])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=12, minute=0, args=[b, "💧 *Água #2 de 3L* — Bebe 500ml agora antes do almoço! 🫙"])
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=12, minute=30, args=[b, "📱 *Instagram — 15 min de engajamento.* Coloca o TIMER antes de abrir. Responde comentários, interage no nicho de beleza. Para quando tocar! ⏱️"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=14, minute=0, args=[b, "🍎 *Frutas do dia!* Você já comeu suas 2-3 frutas hoje? 🍌🍓"])

    # BLOCO ANTI-CIGARRO
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=16, minute=45, args=[b, "🚨 *ALERTA — 17h chegando!* Esse é seu horário de risco.\n\n💡 *Escolhe uma agora:*\n• Liga pro Luigi\n• Toma um chá gelado\n• Faz 20 agachamentos\n• Faz skincare\n• Ouve 1 música que você ama\n\nA vontade passa em 3 minutos. 💪"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=17, minute=0, args=[b, "🚭 *SÃO 17H — NÃO ACENDE!*\n\nRespira fundo: inspire 4 segundos, segura 4, expira 4. Repete 5 vezes agora. 🫁✨"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=17, minute=30, args=[b, "💪 *30 minutos sem fumar!* Se você resistiu, PARABÉNS!\n\nBebe água com gás e ocupa as mãos com algo. 🥂"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=18, minute=0, args=[b, "🌅 *1 hora livre do cigarro!* Como biomédica você sabe: o colágeno da pele melhora em semanas sem nicotina. Isso reflete no seu trabalho! 🌸"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=19, minute=0, args=[b, "🍵 *Ritual noturno saudável — no lugar do cigarro:*\n\n1. Faz seu skincare (10 min)\n2. Coloca uma série ou música\n3. Prepara um chá relaxante\n4. Conversa com Luigi\n\nSubstitui o ritual! 💛"])

    # NOITE
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=20, minute=0, args=[b, "💧 *Água #3 — reta final dos 3L!* Quanto falta pra completar hoje? 🫙"])
    s.add_job(noticia_tarde, "cron", day_of_week="mon-sun", hour=20, minute=30, args=[b])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=21, minute=0, args=[b, "✅ *Revisão do dia:*\n\n1️⃣ O que eu fiz hoje que me orgulho?\n2️⃣ O que eu deixei pra amanhã que não deveria?\n3️⃣ Eu fumei hoje?\n\nEscreve no papel ou só pensa. 🌙"])
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=21, minute=30, args=[b, "📵 *MODO NOTURNO ATIVADO!* Coloca o celular de lado agora.\n\nBoa noite — você foi incrível hoje! 🌙✨"])

    # SEGUNDA-FEIRA
    s.add_job(enviar, "cron", day_of_week="mon", hour=10, minute=50, args=[b, "🧠 *Terapia em 10 minutos!* (11h ao meio-dia)\n\nE a tarefa que a terapeuta passou? Leva anotada! 💬"])
    s.add_job(enviar, "cron", day_of_week="mon", hour=13, minute=0, args=[b, "📚 *TAREFA DA TERAPIA — faz AGORA!*\n\nVocê tem 50 minutos antes do inglês. Abre agora, faz 10 minutos. Timer! ⏱️"])
    s.add_job(enviar, "cron", day_of_week="mon", hour=13, minute=50, args=[b, "🌍 *Aula de inglês em 10 minutos!* (14h às 15h)\n\nYour future self will thank you! 💪"])
    s.add_job(enviar, "cron", day_of_week="mon", hour=15, minute=30, args=[b, "📝 *Tarefa de inglês — faz HOJE!*\n\nAcabou a aula. Enquanto está fresca na memória, faz agora. 20 minutinhos! ⏱️"])

    # TERÇA, QUARTA, QUINTA — CONSULTÓRIO
    s.add_job(enviar, "cron", day_of_week="tue,wed,thu", hour=10, minute=30, args=[b, "📖 *Ebook — 20 minutos AGORA!*\n\nAbre o documento. Escreve sem editar, sem perfeccionismo. O ebook não vai se escrever sozinho! ✍️"])
    s.add_job(enviar, "cron", day_of_week="tue,wed,thu", hour=12, minute=45, args=[b, "👩‍⚕️ *Consultório em 15 minutos!* (13h às 20h)\n\nPega suas coisas e vai com calma. Você vai arrasar hoje! ✨"])

    # QUINTA — SPINNING
    s.add_job(enviar, "cron", day_of_week="thu", hour=6, minute=50, args=[b, "🚴 *Spinning em 10 minutos!* (7h às 8h)\n\nBora pedalar! 💪"])

    # LAVANDERIA
    s.add_job(enviar, "cron", day_of_week="mon,wed,fri", hour=9, minute=0, args=[b, "🧺 *Lavar roupas hoje!* Coloca a máquina antes de sentar pra trabalhar. 💪"])
    s.add_job(enviar, "cron", day_of_week="wed", hour=9, minute=5, args=[b, "🛏️ *Quarta = roupas de cama também!* Troca o lençol e coloca na máquina. Dormir em roupa limpa melhora a pele! 😄"])

    # DUOLINGO FRANCÊS
    s.add_job(enviar, "cron", day_of_week="thu", hour=9, minute=15, args=[b, "🇫🇷 *Duolingo francês — sua lição semanal!*\n\nSó 5-10 minutinhos agora.\n\n*Bonjour, vous êtes incroyable!* 🥐✨"])

    # REMÉDIOS
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=6, minute=55, args=[b, "💊 *REMÉDIOS antes da academia:*\n✅ Finalope (Finasterida) 1mg\n✅ Espironolactona 50mg\n✅ Minoxidil oral 1mg\n✅ Supercof 1 scoop\n✅ Cappuccino Zero 1 scoop"])
    s.add_job(enviar, "cron", day_of_week="mon,fri", hour=7, minute=0, args=[b, "💊 *ROAKI — tomar hoje!* (segunda e sexta — acne) 🌟"])
    s.add_job(enviar, "cron", day_of_week="wed,sun", hour=21, minute=0, args=[b, "💊 *Metronidazol intravaginal — aplicar hoje!* (quarta e domingo) 🌸"])

    # ACOMPANHAMENTO DE METAS
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=9, minute=45, args=[b, "📊 *CHECK DE METAS — Instagram*\n\nHoje você está com quantos seguidores?\n\n🎯 Meta junho: *64.000*\n🎯 Meta julho: *66.000*\n🎯 Meta 2026: *100.000*\n\nManda o número e vai lá no Claude com print do último post! 📱"])
    s.add_job(enviar, "cron", day_of_week="tue", hour=10, minute=15, args=[b, "🎓 *TERÇA = CONTEÚDO EDUCATIVO!*\n\nHook forte nos *primeiros 3 segundos!* Vídeo até 1 minuto. 🎬"])
    s.add_job(enviar, "cron", day_of_week="thu", hour=10, minute=15, args=[b, "🤝 *QUINTA = PARCERIA OU PROCEDIMENTO!*\n\nNão esquece: mencionar collab e cupom quando for parceria! ✅"])
    s.add_job(enviar, "cron", day_of_week="sat", hour=10, minute=15, args=[b, "🌸 *SÁBADO = LIFESTYLE E CONEXÃO!*\n\nConteúdo leve que fideliza. Mostra você como pessoa, não só profissional! 💛"])
    s.add_job(enviar, "cron", day_of_week="fri", hour=20, minute=0, args=[b, "📈 *ANÁLISE DA SEMANA — Instagram*\n\n1️⃣ Quantos posts publicou?\n2️⃣ Qual teve mais views?\n3️⃣ Ganhou ou perdeu seguidores?\n\nManda os prints pro Claude analisar! 🚀"])
    s.add_job(enviar, "cron", day_of_week="sun", hour=9, minute=0, args=[b, "📋 *Domingo — planeja a semana!*\n\n✅ Que conteúdos vou criar?\n✅ Qual dia gravo tudo?\n✅ Tenho tarefa de terapia/inglês pendente?\n\nQuem planeja no domingo não procrastina na segunda! 💡"])
    s.add_job(enviar, "cron", day_of_week="sat", hour=9, minute=0, args=[b, "🌸 *Sábado — dia de recarregar!*\n\nSua única missão: fazer algo que te dá prazer de verdade.\n\nE beber os 3L de água. E comer suas frutas. 😄\n\nVocê trabalhou muito essa semana! ✨"])

    s.start()
    print("✅ Bot completo rodando com todos os lembretes!")

    async with app:
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
