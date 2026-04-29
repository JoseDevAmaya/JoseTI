import win32com.client

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

print("\n=== LISTA DE STORES DETECTADOS ===\n")

for store in outlook.Stores:
    print("Nombre:", store.DisplayName)
    print("  ExchangeStoreType:", getattr(store, "ExchangeStoreType", "N/A"))
    print("  IsDataFileStore:", store.IsDataFileStore)
    print("  IsPrimaryExchangeMailbox:", getattr(store, "IsPrimaryExchangeMailbox", "N/A"))
    print("  RootFolder:", store.GetRootFolder().FolderPath)
    print("--------------------------------------")
