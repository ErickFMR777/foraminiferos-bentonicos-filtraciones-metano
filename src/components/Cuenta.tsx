"use client";

import { useState } from "react";
import { useT } from "@/lib/i18n";

/** El servidor es quien manda sobre este mínimo (`MINIMO_CLAVE` en
 *  `lib/credenciales.ts`). Aquí se repite sólo para avisar antes de enviar. */
const MINIMO = 12;

type Estado =
  | { tipo: "reposo" }
  | { tipo: "enviando" }
  | { tipo: "ok" }
  | { tipo: "error"; clave: string };

export default function Cuenta() {
  const { tx } = useT();
  const [respuesta, setRespuesta] = useState("");
  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [repite, setRepite] = useState("");
  const [estado, setEstado] = useState<Estado>({ tipo: "reposo" });

  const MENSAJES: Record<string, { es: string; en: string }> = {
    respuesta_incorrecta: {
      es: "La respuesta a la pregunta de seguridad no es correcta.",
      en: "The answer to the security question is not correct.",
    },
    actual_incorrecta: {
      es: "La contraseña actual no es correcta.",
      en: "The current password is not correct.",
    },
    corta: {
      es: `La contraseña nueva debe tener al menos ${MINIMO} caracteres.`,
      en: `The new password must be at least ${MINIMO} characters long.`,
    },
    sin_cambio: {
      es: "La contraseña nueva es igual a la actual.",
      en: "The new password is the same as the current one.",
    },
    no_coinciden: {
      es: "La confirmación no coincide con la contraseña nueva.",
      en: "The confirmation does not match the new password.",
    },
    sin_sesion: {
      es: "La sesión ha caducado. Vuelve a entrar.",
      en: "Your session has expired. Please sign in again.",
    },
    sin_credenciales: {
      es: "No se pudo leer el almacén de credenciales.",
      en: "The credential store could not be read.",
    },
    red: {
      es: "No se pudo contactar con el servidor.",
      en: "The server could not be reached.",
    },
  };

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (nueva !== repite) {
      setEstado({ tipo: "error", clave: "no_coinciden" });
      return;
    }
    if (nueva.length < MINIMO) {
      setEstado({ tipo: "error", clave: "corta" });
      return;
    }
    setEstado({ tipo: "enviando" });
    try {
      const r = await fetch("/api/clave", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ actual, nueva, respuesta }),
      });
      if (r.ok) {
        setEstado({ tipo: "ok" });
        setRespuesta("");
        setActual("");
        setNueva("");
        setRepite("");
        return;
      }
      const d = await r.json().catch(() => ({}));
      setEstado({ tipo: "error", clave: String(d?.error ?? "red") });
    } catch {
      setEstado({ tipo: "error", clave: "red" });
    }
  };

  const campo =
    "w-full rounded-[5px] border border-(--border) bg-transparent px-3 py-2 " +
    "text-[0.9rem] text-(--ink) focus-visible:outline-2 " +
    "focus-visible:outline-(--pared-hialino)";
  const etiqueta = "mb-1.5 block text-[0.76rem] text-(--ink-2)";

  return (
    <div className="max-w-[26rem]">
      <form onSubmit={enviar} className="space-y-4">
        <div className="rounded-[6px] border border-(--border) bg-(--surface-2) p-3.5">
          <label className={etiqueta} htmlFor="respuesta">
            {tx({
              es: "Ingresa la respuesta a la pregunta de seguridad para cambiar la contraseña",
              en: "Enter the answer to the security question to change the password",
            })}
          </label>
          <input
            id="respuesta"
            type="password"
            required
            autoComplete="off"
            spellCheck={false}
            value={respuesta}
            onChange={(e) => setRespuesta(e.target.value)}
            className={campo}
          />
          <p className="mt-1.5 text-[0.72rem] text-(--muted)">
            {tx({
              es: "Distingue mayúsculas y minúsculas.",
              en: "Case-sensitive.",
            })}
          </p>
        </div>

        <div>
          <label className={etiqueta} htmlFor="actual">
            {tx({ es: "Contraseña actual", en: "Current password" })}
          </label>
          <input
            id="actual"
            type="password"
            required
            autoComplete="current-password"
            value={actual}
            onChange={(e) => setActual(e.target.value)}
            className={campo}
          />
        </div>

        <div>
          <label className={etiqueta} htmlFor="nueva">
            {tx({ es: "Contraseña nueva", en: "New password" })}
          </label>
          <input
            id="nueva"
            type="password"
            required
            minLength={MINIMO}
            autoComplete="new-password"
            value={nueva}
            onChange={(e) => setNueva(e.target.value)}
            className={campo}
          />
          <p className="mt-1.5 text-[0.72rem] text-(--muted)">
            {tx({
              es: `Mínimo ${MINIMO} caracteres.`,
              en: `At least ${MINIMO} characters.`,
            })}
          </p>
        </div>

        <div>
          <label className={etiqueta} htmlFor="repite">
            {tx({ es: "Repetir la nueva", en: "Repeat the new one" })}
          </label>
          <input
            id="repite"
            type="password"
            required
            autoComplete="new-password"
            value={repite}
            onChange={(e) => setRepite(e.target.value)}
            className={campo}
          />
        </div>

        <div className="pt-1">
          <button
            type="submit"
            disabled={estado.tipo === "enviando"}
            className="rounded-[5px] bg-(--ink) px-4 py-2 text-[0.82rem] font-semibold text-(--surface) transition-opacity hover:opacity-85 disabled:opacity-50"
          >
            {estado.tipo === "enviando"
              ? tx({ es: "Guardando…", en: "Saving…" })
              : tx({ es: "Actualizar contraseña", en: "Update password" })}
          </button>
        </div>
      </form>

      {/* Fuera del formulario anterior a propósito: anidar <form> es HTML
          inválido y el navegador descarta el interior. Envío normal, sin
          JavaScript: el servidor borra la cookie y redirige. */}
      <form method="post" action="/api/salir" className="mt-3">
        <button
          type="submit"
          className="rounded-[5px] border border-(--border) px-4 py-2 text-[0.82rem] text-(--ink-2) transition-colors hover:text-(--ink)"
        >
          {tx({ es: "Cerrar sesión", en: "Sign out" })}
        </button>
      </form>

      <div aria-live="polite" className="mt-4">
        {estado.tipo === "ok" && (
          <p className="rounded-[5px] border border-(--pared-porcelanaceo) px-3 py-2 text-[0.8rem] leading-relaxed text-(--pared-porcelanaceo)">
            {tx({
              es: "Contraseña actualizada. La próxima vez que entres, usa la nueva.",
              en: "Password updated. Use the new one the next time you sign in.",
            })}
          </p>
        )}
        {estado.tipo === "error" && (
          <p className="rounded-[5px] border border-(--pared-aglutinado) px-3 py-2 text-[0.8rem] leading-relaxed text-(--pared-aglutinado)">
            {tx(MENSAJES[estado.clave] ?? MENSAJES.red)}
          </p>
        )}
      </div>

    </div>
  );
}
