const sourceSelect = document.getElementById('source_code');
const targetSelect = document.getElementById('target_code');
const modelInput = document.getElementById('model');
const textInput = document.getElementById('input');
const spinner = document.getElementById('spinner');
const output = document.getElementById('output');
const translateButton = document.getElementById('translate');

function getSelectedOptionText(select) {
  return select.options[select.selectedIndex].text;
}

async function translate() {
  const source_code = sourceSelect.value || 'en';
  const target_code = targetSelect.value || 'de';
  const source_name = getSelectedOptionText(sourceSelect);
  const target_name = getSelectedOptionText(targetSelect);
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

translateButton.addEventListener('click', translate);

document.addEventListener('DOMContentLoaded', () => {
  if (textInput.value.trim()) {
    translate();
  }
});
