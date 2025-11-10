import web.main_web

web_manager = None

def main():
    global web_manager
    web_manager = web.main_web.start()
    
def stop():
    web_manager.stop(fermer=False)
    exit(0)

if __name__ == "__main__":
    main()
