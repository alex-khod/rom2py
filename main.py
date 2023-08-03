from src.mainloop import mainloop

if __name__ == "__main__":
    try:
        mainloop()
    except:
        import traceback
        traceback.print_exc()
        # with open("error.log", "w") as f:
        #     traceback.print_exc(file=f)
