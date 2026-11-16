/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_URL_NUCLEO?: string;
  readonly VITE_URL_PRONOSTICO?: string;
  readonly VITE_URL_SIMULADOR?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
