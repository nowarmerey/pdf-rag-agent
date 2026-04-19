const LANG_KEY = "lexai_lang";

function setLang(lang) {
  localStorage.setItem(LANG_KEY, lang);

  // تحديث كل العناصر
  document.querySelectorAll("[data-de]").forEach((el) => {
    el.textContent = el.getAttribute(`data-${lang}`) || el.textContent;
  });

  // تحديث الـ placeholders
  document.querySelectorAll("[data-de-placeholder]").forEach((el) => {
    el.placeholder =
      el.getAttribute(`data-${lang}-placeholder`) || el.placeholder;
  });

  // تحديث الأزرار
  document.querySelectorAll(".lang-btn, .lang-btn-sm").forEach((btn) => {
    btn.classList.remove("active");
  });
  const activeBtn = document.getElementById(`btn-${lang}`);
  if (activeBtn) activeBtn.classList.add("active");

  // تحديث direction
  document.documentElement.lang = lang;
}

function getLang() {
  return localStorage.getItem(LANG_KEY) || "de";
}

// تطبيق اللغة عند تحميل الصفحة
document.addEventListener("DOMContentLoaded", () => {
  setLang(getLang());
});
