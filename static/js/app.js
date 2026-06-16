const sourceSelect = document.getElementById('source_code');
const targetSelect = document.getElementById('target_code');
const sourceVariantSelect = document.getElementById('source_variant');
const targetVariantSelect = document.getElementById('target_variant');
const swapButton = document.getElementById('swap-languages');
const modelInput = document.getElementById('model');
const textInput = document.getElementById('input');
const spinner = document.getElementById('spinner');
const output = document.getElementById('output');
const translateButton = document.getElementById('translate');

function getSelectedOptionText(select) {
  return select.options[select.selectedIndex].text;
}

function syncPrimarySelectors(sourceCode, targetCode) {
  sourceSelect.value = sourceCode;
  targetSelect.value = targetCode;
  updateVariantOptions(sourceCode, sourceVariantSelect);
  updateVariantOptions(targetCode, targetVariantSelect);
}

function populateSelect(select, items, selectedValue) {
  select.innerHTML = '';
  items.forEach(item => {
    const option = document.createElement('option');
    option.value = item.code;
    option.textContent = item.name;
    if (item.code === selectedValue) {
      option.selected = true;
    }
    select.appendChild(option);
  });
}

function updateVariantOptions(baseCode, variantSelect) {
  const variants = window.languageVariants?.[baseCode] || [];
  const selectedValue = variants.length ? variants[0].code : baseCode;
  populateSelect(variantSelect, variants.length ? variants : [{ code: baseCode, name: 'Default variant' }], selectedValue);
}

async function translate() {
  const source_code = sourceVariantSelect.value || 'de-DE';
  const target_code = targetVariantSelect.value || 'en-US';
  const source_name = getSelectedOptionText(sourceVariantSelect);
  const target_name = getSelectedOptionText(targetVariantSelect);
  const model = modelInput.value || 'translategemma:12b';
  const text = textInput.value;
  output.value = '';
  if (!text.trim()) {
    alert('Please enter text to translate');
    return;
  }
  spinner.style.display = 'block';

  try {
    const resp = await fetch('/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_code, target_code, source_name, target_name, text, model }),
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      output.value = data.translation;
    } else {
      output.value = 'Error: ' + (data.error || 'unknown');
    }
  } catch (e) {
    output.value = 'Error: ' + e;
  } finally {
    spinner.style.display = 'none';
  }
}

swapButton.addEventListener('click', () => {
  const newSource = targetSelect.value;
  const newTarget = sourceSelect.value;
  syncPrimarySelectors(newSource, newTarget);
});


sourceSelect.addEventListener('change', () => {
  updateVariantOptions(sourceSelect.value, sourceVariantSelect);
});

targetSelect.addEventListener('change', () => {
  updateVariantOptions(targetSelect.value, targetVariantSelect);
});

translateButton.addEventListener('click', translate);

document.addEventListener('DOMContentLoaded', () => {
  updateVariantOptions(sourceSelect.value, sourceVariantSelect);
  updateVariantOptions(targetSelect.value, targetVariantSelect);
});
