from src.whisperdesk.core.settings.settings_manager import SettingsManager

manager = SettingsManager()
print("Current settings:")
print(manager.settings)

print("\nUpdating whisper_model_size to 'small'...")
manager.update(whisper_model_size="small")

print("\nReloading from disk to confirm it persisted...")
manager2 = SettingsManager()
print(manager2.settings)