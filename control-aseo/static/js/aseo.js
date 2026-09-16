async function subirFoto(inputEl, sesionId, nombreItem) {
    const archivo = inputEl.files[0];
    if (!archivo) return;

    const tarjeta = inputEl.closest(".item");
    const estadoEl = tarjeta.querySelector(".estado-analisis");
    const badgeEl = tarjeta.querySelector(".badge-item");

    estadoEl.classList.remove("oculto");
    estadoEl.textContent = "Analizando con IA local...";
    badgeEl.textContent = "Analizando...";
    badgeEl.className = "badge badge-item";

    const formData = new FormData();
    formData.append("foto", archivo);

    try {
        const resp = await fetch(
            `/aseo/${sesionId}/foto/${encodeURIComponent(nombreItem)}`,
            { method: "POST", body: formData }
        );
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || "Error al analizar la foto.");
        }
        const datos = await resp.json();

        badgeEl.textContent = datos.nivel;
        badgeEl.className = `badge badge-item badge-${datos.nivel.toLowerCase()}`;

        let miniatura = tarjeta.querySelector(".miniatura");
        if (!miniatura) {
            miniatura = document.createElement("img");
            miniatura.className = "miniatura";
            tarjeta.insertBefore(miniatura, tarjeta.querySelector(".input-foto") || tarjeta.querySelector(".estado-analisis"));
        }
        miniatura.src = `${datos.foto_url}?t=${Date.now()}`;

        let retroEl = tarjeta.querySelector(".retro");
        if (!retroEl) {
            retroEl = document.createElement("p");
            retroEl.className = "retro";
            tarjeta.insertBefore(retroEl, estadoEl);
        }
        retroEl.textContent = datos.retroalimentacion;

        let motorEl = tarjeta.querySelector(".motor");
        if (!motorEl) {
            motorEl = document.createElement("p");
            motorEl.className = "motor";
            tarjeta.insertBefore(motorEl, estadoEl);
        }
        motorEl.textContent = `Analizado con: ${datos.motor_ia}`;

        estadoEl.classList.add("oculto");
    } catch (e) {
        estadoEl.textContent = "Error: " + e.message;
        badgeEl.textContent = "Error";
    }
}
