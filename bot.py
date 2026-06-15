import os
import asyncio
import httpx
import pytz
from telegram import Bot
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

# ─── RESUMO MATINAL INTELIGENTE (IA) ───
async def resumo_matinal(bot: Bot):
    msg = await chamar_claude("""Você é assistente pessoal de uma biomédica brasileira, tricologista, especialista em harmonização facial e skincare, com 60k seguidores no Instagram. Ela também está aprendendo inglês e francês.

Crie um resumo matinal COMPLETO e REAL para hoje com exatamente estas seções:

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

# ─── IDEIA DE CONTEÚDO DO DIA (IA) ───
async def ideia_conteudo(bot: Bot):
    msg = await chamar_claude("""Sugira UMA ideia de conteúdo para Instagram/TikTok para uma biomédica e tricologista brasileira especializada em skincare, harmonização facial e cuidados capilares.

Formato da resposta:
📸 *CONTEÚDO DO DIA*
*Tipo:* (Reels / Carrossel / Story)
*Título:* ...
*Hook:* (primeira frase que prende atenção)
*Roteiro rápido:* (3 pontos do que falar)
*Legenda sugerida:* (com emojis e hashtags do nicho)

Seja criativa, atual e baseada em tendências reais de 2025/2026.""")
    await enviar(bot, msg)

# ─── NOTÍCIA DA TARDE (IA) ───
async def noticia_tarde(bot: Bot):
    msg = await chamar_claude("""Dê um update rápido de 2 notícias importantes que aconteceram hoje no mundo. Seja direta e real. Use emojis. Máximo 100 palavras.""")
    await enviar(bot, f"📰 *Update da tarde:*\n\n{msg}")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌸 *Olá! Sou sua assistente pessoal!*\n\nUse /id para pegar seu Chat ID e ativar os lembretes.",
        parse_mode="Markdown"
    )

async def get_id(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Seu Chat ID é: `{chat_id}`", parse_mode="Markdown")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))

    s = AsyncIOScheduler(timezone=FUSO)
    b = app.bot

    # ══════════════════════════════════════
    # TODOS OS DIAS
    # ══════════════════════════════════════

    # 7h — Resumo matinal com IA
    s.add_job(resumo_matinal, "cron", day_of_week="mon-sun", hour=7, minute=0, args=[b])

    # 7h10 — Intenção do dia
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=7, minute=10, args=[b,
        "📝 *Intenção do dia:* Antes de abrir qualquer rede social — escreve no papel 1 objetivo pra hoje. O que você precisa ter feito quando a cabeça tocar o travesseiro? ✨"])

    # 8h — Academia (seg-sex)
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=8, minute=0, args=[b,
        "🏋️ *ACADEMIA — AGORA!* Das 8h às 9h. Pré-treino tomado, sem desculpa! 💪"])

    # 8h05 — WhatsApp na esteira
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=8, minute=5, args=[b,
        "📱 *Você está na esteira?* Abre o WhatsApp AGORA e responde as mensagens por *10 minutos*. Coloca o timer! ⏱️\n\nDepois fecha e foca no treino. 💪"])

    # 9h30 — Água (1° copo do dia)
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=9, minute=30, args=[b,
        "💧 *Água #1 de 3L* — Você já bebeu pelo menos 500ml hoje? Pega a garrafinha agora! Sua pele e seus rins agradecem. 🫙"])

    # 10h — Ideia de conteúdo com IA (seg-sex)
    s.add_job(ideia_conteudo, "cron", day_of_week="mon-fri", hour=10, minute=0, args=[b])

    # 12h — Água #2
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=12, minute=0, args=[b,
        "💧 *Água #2 de 3L* — Já passou da metade da manhã. Como está sua hidratação? Bebe 500ml agora antes do almoço! 🫙"])

    # 12h30 — Engajamento Instagram (seg-sex)
    s.add_job(enviar, "cron", day_of_week="mon-fri", hour=12, minute=30, args=[b,
        "📱 *Instagram — 15 min de engajamento.* Coloca o TIMER antes de abrir. Responde comentários, interage no nicho de beleza/estética. Para quando tocar! ⏱️"])

    # 14h — Frutas do dia
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=14, minute=0, args=[b,
        "🍎 *Frutas do dia!* Você já comeu suas 2-3 frutas hoje? Se não, esse é o momento perfeito. Banana, maçã, mamão, morango — escolhe 2 agora! 🍌🍓"])

    # ══════════════════════════════════════
    # BLOCO ANTI-CIGARRO — 17h É O MOMENTO CRÍTICO
    # ══════════════════════════════════════

    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=16, minute=45, args=[b,
        "🚨 *ALERTA — 17h chegando!* Esse é o seu horário de risco. Vamos quebrar esse ciclo HOJE.\n\n💡 *Escolhe uma agora:*\n• Faz uma ligação pro seu marido\n• Toma um chá gelado com limão\n• Faz 20 agachamentos\n• Pinta as unhas / faz skincare\n• Coloca fone e ouve 1 música que você ama\n\nA vontade passa em 3 minutos. Você é mais forte que ela. 💪"])

    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=17, minute=0, args=[b,
        "🚭 *SÃO 17H — NÃO ACENDE!*\n\nRespira fundo: inspire 4 segundos, segura 4, expira 4.\n\nRepete 5 vezes agora mesmo.\n\nSeu corpo não precisa do cigarro. Ele precisa de oxigênio. 🫁✨"])

    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=17, minute=30, args=[b,
        "💪 *30 minutos sem fumar!* Se você resistiu até agora, PARABÉNS — você provou que consegue.\n\nBebe um copo d'água com gás (simula a sensação do cigarro) e ocupa as mãos com algo: celular, livro, cozinha, qualquer coisa. 🥂"])

    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=18, minute=0, args=[b,
        "🌅 *1 hora livre do cigarro!* Cada dia que você resiste é um dia que seus pulmões, sua pele e seu cabelo agradecem.\n\nComo biomédica você sabe: o colágeno da pele melhora em semanas sem nicotina. Isso reflete no seu trabalho e na sua autoestima. 🌸"])

    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=19, minute=0, args=[b,
        "🍵 *Ritual noturno saudável — no lugar do cigarro:*\n\n1. Faz seu skincare agora (10 min)\n2. Coloca uma série ou música\n3. Prepara um chá relaxante\n4. Conversa com seu marido\n\nO cigarro era um ritual. Substitui o ritual, não apenas o cigarro. 💛"])

    # ══════════════════════════════════════
    # NOITE
    # ══════════════════════════════════════

    # 20h — Água #3
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=20, minute=0, args=[b,
        "💧 *Água #3 — reta final dos 3L!* Quanto falta pra completar sua meta hoje? Bebe pelo menos mais 500ml antes de dormir. 🫙"])

    # 20h30 — Notícia da tarde com IA
    s.add_job(noticia_tarde, "cron", day_of_week="mon-sun", hour=20, minute=30, args=[b])

    # 21h — Revisão do dia
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=21, minute=0, args=[b,
        "✅ *Revisão do dia — 2 minutinhos:*\n\n1️⃣ O que eu fiz hoje que me orgulho?\n2️⃣ O que eu deixei pra amanhã que não deveria?\n3️⃣ Eu fumei hoje? (Seja honesta consigo)\n\nEscreve no papel ou só pensa. Isso cria consciência e combate a procrastinação. 🌙"])

    # 21h30 — Modo noturno
    s.add_job(enviar, "cron", day_of_week="mon-sun", hour=21, minute=30, args=[b,
        "📵 *MODO NOTURNO ATIVADO!* Coloca o celular de lado agora.\n\nCelular embaixo da almofada não conta como descanso. 😄\n\nBoa noite — você foi incrível hoje! 🌙✨"])

    # ══════════════════════════════════════
    # SEGUNDA-FEIRA
    # ══════════════════════════════════════

    s.add_job(enviar, "cron", day_of_week="mon", hour=10, minute=50, args=[b,
        "🧠 *Terapia em 10 minutos!* (11h ao meio-dia)\n\nE a tarefa que a terapeuta passou? Se não fez, tudo bem — mas leva anotada pra contar. A terapia só funciona se você faz a parte de fora também. 💬"])

    s.add_job(enviar, "cron", day_of_week="mon", hour=13, minute=0, args=[b,
        "📚 *TAREFA DA TERAPIA — faz AGORA!*\n\nVocê tem 50 minutos antes da aula de inglês. A procrastinação começa com 'depois'. Abre agora, faz 10 minutos. Só 10. ⏱️"])

    s.add_job(enviar, "cron", day_of_week="mon", hour=13, minute=50, args=[b,
        "🌍 *Aula de inglês em 10 minutos!* (14h às 15h)\n\nE o dever de casa? Se não fez, faz agora nos 10 min que têm. Qualquer coisa é melhor que nada. Your future self will thank you! 💪"])

    s.add_job(enviar, "cron", day_of_week="mon", hour=15, minute=30, args=[b,
        "📝 *Tarefa de inglês — faz HOJE!*\n\nAcabou a aula. Enquanto ainda está fresca na memória, faz a tarefa agora. 20 minutinhos. Coloca o timer! ⏱️\n\nQuem faz a lição aprende 3x mais rápido. 🌍"])

    # ══════════════════════════════════════
    # TERÇA, QUARTA, QUINTA — DIAS DE CONSULTÓRIO
    # ══════════════════════════════════════

    s.add_job(enviar, "cron", day_of_week="tue,wed,thu", hour=10, minute=30, args=[b,
        "📖 *EBOOK — 20 minutos AGORA!*\n\nAbre o documento. Escreve sem editar, sem perfeccionismo. Qualquer palavra que sair está ótima.\n\nO ebook não vai se escrever sozinho. Você tem 20 min antes do consultório. Timer já! ⏱️✍️"])

    s.add_job(enviar, "cron", day_of_week="tue,wed,thu", hour=12, minute=45, args=[b,
        "👩‍⚕️ *Consultório em 15 minutos!* (13h às 20h)\n\nPega suas coisas, se arruma e vai com calma. Você vai arrasar hoje! ✨"])

    # ══════════════════════════════════════
    # LAVANDERIA
    # ══════════════════════════════════════

    s.add_job(enviar, "cron", day_of_week="mon,wed,fri", hour=9, minute=0, args=[b,
        "🧺 *Lavar roupas hoje!* Coloca a máquina antes de sentar pra trabalhar — assim ela lava enquanto você produz. Eficiência pura! 💪"])

    s.add_job(enviar, "cron", day_of_week="wed", hour=9, minute=5, args=[b,
        "🛏️ *Quarta = roupas de cama também!* Troca o lençol e coloca na máquina. Dormir em roupa de cama limpa melhora o sono e a pele. Você sabe disso melhor que ninguém! 😄"])

    # ══════════════════════════════════════
    # DUOLINGO FRANCÊS — QUINTA
    # ══════════════════════════════════════

    s.add_job(enviar, "cron", day_of_week="thu", hour=9, minute=15, args=[b,
        "🇫🇷 *Duolingo francês — sua lição semanal!*\n\nSó 5-10 minutinhos. Abre o app agora antes de começar o dia.\n\n*Bonjour, vous êtes incroyable!* 🥐✨\n(Bom dia, você é incrível!)"])

    # ══════════════════════════════════════
    # FIM DE SEMANA — MAIS LEVE
    # ══════════════════════════════════════

    s.add_job(enviar, "cron", day_of_week="sat", hour=9, minute=0, args=[b,
        "🌸 *Sábado — dia de recarregar!*\n\nSua única missão hoje: fazer algo que te dá prazer de verdade.\n\nE beber os 3L de água. E comer suas frutas. 😄\n\nVocê trabalhou muito essa semana. Merece descansar com intenção! ✨"])

    s.add_job(enviar, "cron", day_of_week="sun", hour=9, minute=0, args=[b,
        "📋 *Domingo — planeja a semana!*\n\nDedica 15 min agora pra:\n✅ Que conteúdos vou criar?\n✅ Qual dia vou escrever o ebook?\n✅ Tenho tarefa de terapia/inglês pendente?\n\nQuem planeja no domingo, não procrastina na segunda. 💡"])

    s.start()
    print("✅ Bot completo rodando!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
