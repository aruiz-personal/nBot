from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import yaml, logging, os
import extract
import pdf_to_text
import telegram

INPUT_TEXT,INPUT_TEXT_C = range(2) 
text = ""
INPUT_PDF, INPUT_PDF_C = range(2)
GRUPO = "YOUR GROUP OR CHAT ID"

""" Funciones """
def start(update, context):
    if(update.message.chat.id!=GRUPO): return
    logger.info('He recibido un comando start')
    update.message.reply_text('¡Bienvenido a nBot %s!. Opciones disponibles: \
    \n/ioc - Cargar indicadores modo texto. \
    \n/pdf - Cargar indicadores pdf. \
    \n' % update.message.from_user.name)

def ioc(update, context):   
    if(update.message.chat.id!=GRUPO): return 
    update.message.reply_text('Bueno %s, pasame el mensaje asi lo parseo!' % update.message.from_user.name)
    return INPUT_TEXT

def pdf(update, context):  
    if(update.message.chat.id!=GRUPO): return   
    update.message.reply_text('Bueno %s, pasame el documento pdf asi lo parseo!' % update.message.from_user.name)
    return INPUT_PDF

def get_destination_path(path, file_url):
    down_file = os.path.join(path, os.path.basename(file_url))
    new_file = os.path.join(path, os.path.splitext(
                os.path.basename(file_url))[0]) + '.pdf'
    return down_file, new_file

def check_document(file_name):
    return file_name.endswith('.pdf')

def document_saver(update,context):
    if(update.message.chat.id!=GRUPO): return
    global text
    if update.message.document and check_document(update.message.document.file_name):
        doc_file = context.bot.get_file(update.message.document.file_id)
        my_path = os.path.abspath(os.path.dirname(__file__))
        down, new = get_destination_path(my_path, update.message.document.file_name)
        doc = doc_file.download(down)
        text=pdf_to_text.convertir(doc)
        if os.path.exists(doc):
            os.remove(doc)
        cantidad = extract.contar(text) 
        if(cantidad==0):
           update.message.reply_text('%s, no encuentro IoC válidos en el documento %s. Recordá que solo acepto SHA1, IPs públicas y dominios' % (update.message.from_user.name, update.message.document.file_name))
        if(cantidad>0 and cantidad <= 25):
           update.message.reply_text('Se recibieron los IoC de %s, procederé a cargar en nuestras soluciones lo siguiente:\n%s\n ¿Confirmar? /si - /no' % (update.message.document.file_name, extract.buscar(text)))
         
        if(cantidad >25):
            update.message.reply_text('Se recibieron %i IoC (no puedo listar en este chat esta cantidad) de %s, procederé a cargarlos en nuestras soluciones de seguridad. \n ¿Confirmar? /si - /no' % (cantidad, update.message.document.file_name))
         
        if(cantidad>0):
            return INPUT_PDF_C
    return ConversationHandler.END    

def confirmar(update,context):
    if(update.message.chat.id!=GRUPO): return
    global text
    if(update.message.text=="/si"):
        extract.extraer(text)
        #update.message.reply_text('%s, confirmado, se cargaron!' % update.message.from_user.name)
        update.message.reply_text('%s, entiendo tu confirmación, pero aun no estoy autorizado a cargar IoC de pdfs!' % update.message.from_user.name)
    if(update.message.text=="/no"):
        update.message.reply_text('%s, se anulo la carga!' % update.message.from_user.name)
    text=""
    return ConversationHandler.END

def confirmar_ioc(update,context):
    if(update.message.chat.id!=GRUPO): return
    global text
    if(update.message.text=="/si"):
        extract.extraer(text)
        #update.message.reply_text('%s, confirmado, se cargaron!' % update.message.from_user.name)
        update.message.reply_text('%s, confirmado, se cargaron los IoC' % update.message.from_user.name)
    if(update.message.text=="/no"):
        update.message.reply_text('%s, se anulo la carga!' % update.message.from_user.name)
    text=""
    return ConversationHandler.END

def updateIoc(update, context):  
    if(update.message.chat.id!=GRUPO): return
    global text  
    text = update.message.text 
    if(extract.buscar(text) != ""):
        update.message.reply_text('Se recibieron los IoC, procederé a cargar en nuestras soluciones lo siguiente:\n%s\n ¿Confirmar? /si - /no' % extract.buscar(text))
    else:
        update.message.reply_text('No encuentro IoC válidos en tu mensaje %s. Recordá que solo acepto SHA1, IPs públicas y dominios' % update.message.from_user.name)
        return ConversationHandler.END

    return INPUT_TEXT_C
    

""" Main del Programa """
if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger('nAutomaticBot')
    
    """ Llave API para conectarse a Telegram """
    updater = Updater(token="YOUR BOTS TOKEN", use_context=True)

    dp = updater.dispatcher

    """ Handler's """
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('ioc', ioc)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, updateIoc)],
            INPUT_TEXT_C: [MessageHandler(Filters.command, confirmar_ioc)]
        },
        fallbacks=[]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('pdf', pdf)
        ],
        states={
            INPUT_PDF: [MessageHandler(Filters.document, document_saver)], 
            INPUT_PDF_C: [MessageHandler(Filters.command, confirmar)]         
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()
