import argostranslate.package
import argostranslate.translate


class Translator:
    def __init__(self, from_code: str = "en", to_code: str = "ar"):
        self.from_code = from_code
        self.to_code = to_code
        self._ensure_language_pack_installed()

    def _ensure_language_pack_installed(self) -> None:
        """Downloads the specific language pair model if not already
        installed. Only needs to happen once ever, cached after."""
        installed_languages = argostranslate.translate.get_installed_languages()
        installed_codes = {lang.code for lang in installed_languages}

        if self.from_code in installed_codes and self.to_code in installed_codes:
            return  # already installed, nothing to do

        print(f"Downloading translation model ({self.from_code} -> {self.to_code})...")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        package_to_install = next(
            pkg for pkg in available_packages
            if pkg.from_code == self.from_code and pkg.to_code == self.to_code
        )
        argostranslate.package.install_from_path(package_to_install.download())

    def translate(self, text: str) -> str:
        if not text.strip():
            return ""
        return argostranslate.translate.translate(text, self.from_code, self.to_code)