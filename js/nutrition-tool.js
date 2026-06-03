(function () {
    'use strict';

    var PREFIX = 'tool-';
    var API = '/api/food.php';

    var $ = function (id) {
        return document.getElementById(PREFIX + id);
    };

    var els = {};
    var mealItems = [];
    var selectedFood = null;
    var dailyGoal = 2000;
    var searchResults = [];
    var detailRequestId = 0;

    var TYPE_LABELS = {
        standard: 'Whole food',
        packaged: 'Packaged',
        branded: 'Branded',
        general: 'Common food'
    };

    var TYPE_CLASS = {
        standard: 'type-standard',
        packaged: 'type-packaged',
        branded: 'type-branded',
        general: 'type-general'
    };

    function cacheDom() {
        els = {
            searchInput: $('search-input'),
            searchBtn: $('search-btn'),
            barcodeInput: $('barcode-input'),
            barcodeBtn: $('barcode-btn'),
            loader: $('loader'),
            error: $('error'),
            resultsBox: $('results'),
            servingArea: $('serving-area'),
            qtyInput: $('qty'),
            servingSelect: $('serving-sel'),
            addBtn: $('add-btn'),
            previewCal: $('preview-cal'),
            totalCal: $('total-cal'),
            totalPro: $('total-pro'),
            totalCarb: $('total-carb'),
            totalFat: $('total-fat'),
            totalFiber: $('total-fiber'),
            totalSugar: $('total-sugar'),
            totalSodium: $('total-sodium'),
            totalSatFat: $('total-satfat'),
            totalCholesterol: $('total-chol'),
            totalPotassium: $('total-potassium'),
            proPct: $('pro-pct'),
            carbPct: $('carb-pct'),
            fatPct: $('fat-pct'),
            proSeg: $('pro-seg'),
            carbSeg: $('carb-seg'),
            fatSeg: $('fat-seg'),
            goalBar: $('goal-bar'),
            goalPct: $('goal-pct'),
            goalEaten: $('goal-eaten'),
            goalDisplay: $('goal-display'),
            goalInput: $('goal-input'),
            goalSetBtn: $('goal-set'),
            tableBody: $('table-body'),
            tableFoot: $('table-foot'),
            tableWrap: $('table-wrap'),
            emptyState: $('empty'),
            clearBtn: $('clear-btn'),
            sourceInfo: $('source-info'),
            selectedName: $('selected-name'),
            selectedInfo: $('selected-info'),
            detailPanel: $('detail-panel'),
            itemCount: $('item-count')
        };
    }

    function init() {
        cacheDom();
        loadState();
        bindEvents();
        setFlowStep(1);
        updateUI();
    }

    function setFlowStep(step) {
        document.querySelectorAll('#nutrition-tool .tool-flow-step').forEach(function (el) {
            el.classList.toggle('is-active', el.getAttribute('data-step') === String(step));
        });
    }

    function loadState() {
        try {
            var saved = localStorage.getItem('mmMealItems');
            if (saved) {
                mealItems = JSON.parse(saved);
                mealItems = mealItems.map(function (m) {
                    if (m.name) {
                        m.name = displayName(String(m.name).replace(/\s*\([^)]*\)\s*$/, '').trim());
                    }
                    return m;
                });
            }
            var g = localStorage.getItem('mmCalorieGoal');
            if (g) {
                dailyGoal = parseInt(g, 10) || 2000;
            }
        } catch (e) {
            mealItems = [];
        }
    }

    function saveState() {
        try {
            localStorage.setItem('mmMealItems', JSON.stringify(mealItems));
            localStorage.setItem('mmCalorieGoal', String(dailyGoal));
        } catch (e) { /* ignore */ }
    }

    function bindEvents() {
        if (els.searchBtn) {
            els.searchBtn.addEventListener('click', doSearch);
        }
        if (els.searchInput) {
            els.searchInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    doSearch();
                }
            });
        }
        if (els.barcodeBtn) {
            els.barcodeBtn.addEventListener('click', searchBarcode);
        }
        if (els.barcodeInput) {
            els.barcodeInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    searchBarcode();
                }
            });
        }
        if (els.addBtn) {
            els.addBtn.addEventListener('click', addFood);
        }
        if (els.qtyInput) {
            els.qtyInput.addEventListener('input', updateServingPreview);
        }
        if (els.servingSelect) {
            els.servingSelect.addEventListener('change', updateServingPreview);
        }
        if (els.clearBtn) {
            els.clearBtn.addEventListener('click', function () {
                if (confirm('Clear all items from this meal?')) {
                    mealItems = [];
                    updateUI();
                    showToast('Meal cleared');
                }
            });
        }
        if (els.goalSetBtn) {
            els.goalSetBtn.addEventListener('click', setGoal);
        }
        if (els.goalInput) {
            els.goalInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    setGoal();
                }
            });
        }
        var cancelBtn = document.getElementById('tool-add-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', cancelAddSelection);
        }
        document.querySelectorAll('.tool-qty-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (!els.qtyInput) return;
                var delta = parseFloat(btn.getAttribute('data-qty-delta')) || 0;
                var v = (parseFloat(els.qtyInput.value) || 1) + delta * 0.5;
                els.qtyInput.value = String(Math.max(0.1, Math.round(v * 10) / 10));
                updateServingPreview();
            });
        });
        document.querySelectorAll('[data-goal]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var v = parseInt(btn.getAttribute('data-goal'), 10);
                if (v >= 500) {
                    dailyGoal = v;
                    if (els.goalInput) {
                        els.goalInput.value = String(v);
                    }
                    saveState();
                    updateUI();
                    showToast('Daily goal set to ' + v + ' kcal');
                }
            });
        });
    }

    function displayName(name) {
        var n = (name || 'Unknown').trim();
        if (n.length > 72) {
            n = n.substring(0, 69) + '…';
        }
        return n;
    }

    function parseItem(item) {
        var nuts = item.nutrients || {};
        var name = displayName(item.name || 'Unknown');
        var servingText = item.serving || '100g';
        var servingG = item.servingGrams;
        if (servingG == null || servingG <= 0) {
            servingG = parseServingG(servingText);
        }
        var labelServingG = item.labelServingGrams;
        if (labelServingG == null || labelServingG <= 0) {
            labelServingG = null;
        }
        return {
            id: item.id,
            fdcId: item.fdcId || null,
            name: name,
            foodType: item.foodType || 'standard',
            serving: servingText,
            serving_g: servingG,
            label_serving_g: labelServingG,
            calories: r2(nuts.calories),
            protein: r2(nuts.protein),
            carbs: r2(nuts.carbs),
            fat: r2(nuts.fat),
            fiber: r2(nuts.fiber),
            sugar: r2(nuts.sugars),
            sodium: r2(nuts.sodium),
            saturated_fat: r2(nuts.saturated_fat),
            cholesterol: r2(nuts.cholesterol),
            potassium: r2(nuts.potassium),
            portions: item.portions || null
        };
    }

    function doSearch() {
        var q = (els.searchInput && els.searchInput.value || '').trim();
        if (!q) {
            showError('Enter a food name to search.');
            return;
        }
        resetSelectionUI();
        setFlowStep(1);
        showEl(els.loader);
        hideEl(els.error);
        setStatus('Searching…');

        fetch(API + '?query=' + encodeURIComponent(q))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                hideEl(els.loader);
                if (!data || !data.success || !data.data || !data.data.length) {
                    showError('No foods found. Try chicken breast, banana, or brown rice.');
                    return;
                }
                searchResults = data.data.map(parseItem);
                renderResults(searchResults);
                setStatus('Found ' + searchResults.length + ' matching foods');
            })
            .catch(function () {
                hideEl(els.loader);
                showError('Search failed. Check your connection and try again.');
            });
    }

    function searchBarcode() {
        var code = (els.barcodeInput && els.barcodeInput.value || '').trim();
        if (!code) {
            showError('Enter a product barcode.');
            return;
        }
        resetSelectionUI();
        showEl(els.loader);
        hideEl(els.error);
        setStatus('Looking up product…');

        fetch(API + '?barcode=' + encodeURIComponent(code))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                hideEl(els.loader);
                if (!data || !data.success || !data.data) {
                    showError('No product found for that barcode.');
                    return;
                }
                setStatus('Product found — adjust serving and add to meal');
                selectFood(parseItem(data.data), null);
                hideEl(els.resultsBox);
            })
            .catch(function () {
                hideEl(els.loader);
                showError('Barcode lookup failed. Try again.');
            });
    }

    function renderResults(foods) {
        if (!els.resultsBox) {
            return;
        }
        els.resultsBox.innerHTML = '';
        foods.forEach(function (f) {
            var div = document.createElement('button');
            div.type = 'button';
            div.className = 'tool-result';
            var typeKey = f.foodType || 'standard';
            var label = TYPE_LABELS[typeKey] || 'Food';
            var cls = TYPE_CLASS[typeKey] || 'type-standard';
            div.innerHTML =
                '<div class="tool-result-top">' +
                '<span class="tool-result-name">' + escHtml(displayName(f.name)) + '</span>' +
                '<span class="tool-result-badge ' + cls + '">' + escHtml(label) + '</span>' +
                '</div>' +
                '<div class="tool-result-macros">' +
                pill('cal', (f.calories || 0) + ' kcal') +
                pill('pro', (f.protein || 0) + 'g P') +
                pill('carb', (f.carbs || 0) + 'g C') +
                pill('fat', (f.fat || 0) + 'g F') +
                '</div>';
            div.addEventListener('click', function () {
                selectFood(f, div);
            });
            els.resultsBox.appendChild(div);
        });
        showEl(els.resultsBox);
    }

    function pill(kind, text) {
        return '<span class="tool-pill ' + kind + '">' + escHtml(text) + '</span>';
    }

    function selectFood(f, el) {
        setFlowStep(2);
        if (els.resultsBox) {
            els.resultsBox.querySelectorAll('.tool-result').forEach(function (node) {
                node.classList.remove('selected');
            });
        }
        if (el) {
            el.classList.add('selected');
        }

        selectedFood = {
            name: f.name,
            cal: f.calories || 0,
            pro: f.protein || 0,
            carb: f.carbs || 0,
            fat: f.fat || 0,
            fiber: f.fiber || 0,
            sugar: f.sugar || 0,
            sodium: f.sodium || 0,
            potassium: f.potassium || 0,
            cholesterol: f.cholesterol || 0,
            saturatedFat: f.saturated_fat || 0,
            servingG: f.serving_g || 100,
            fdcId: f.fdcId || null,
            servings: [{ desc: '100 g (standard)', size: 100 }]
        };

        var labelG = f.label_serving_g;
        if (labelG && Math.abs(labelG - 100) > 0.5) {
            var hasServing = selectedFood.servings.some(function (s) {
                return Math.abs(s.size - labelG) < 0.5;
            });
            if (!hasServing) {
                selectedFood.servings.push({
                    desc: (f.serving || 'Label serving') + ' (' + labelG + ' g)',
                    size: labelG
                });
            }
        }

        if (els.addBtn) {
            els.addBtn.disabled = true;
        }
        if (els.selectedName) {
            els.selectedName.textContent = 'Loading…';
        }
        showAddPanel(true);

        if (f.fdcId) {
            var reqId = ++detailRequestId;
            fetch(API + '?fdcId=' + encodeURIComponent(f.fdcId))
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (reqId !== detailRequestId) {
                        return;
                    }
                    if (data && data.success && data.data) {
                        applyDetail(data.data);
                    }
                    finishServingUI();
                })
                .catch(function () {
                    if (reqId === detailRequestId) {
                        finishServingUI();
                    }
                });
        } else if (f.portions && f.portions.length) {
            selectedFood.servings = f.portions.map(function (p) {
                return { desc: p.desc, size: p.grams || p.size || 100 };
            });
            finishServingUI();
        } else {
            finishServingUI();
        }
    }

    function pickNutrient(nuts, key, fallback) {
        if (nuts[key] !== undefined && nuts[key] !== null && nuts[key] !== '') {
            return r2(nuts[key]);
        }
        return fallback;
    }

    function applyDetail(detail) {
        var nuts = detail.nutrients || {};
        if (detail.name) {
            selectedFood.name = displayName(detail.name);
        }
        selectedFood.cal = pickNutrient(nuts, 'calories', selectedFood.cal);
        selectedFood.pro = pickNutrient(nuts, 'protein', selectedFood.pro);
        selectedFood.carb = pickNutrient(nuts, 'carbs', selectedFood.carb);
        selectedFood.fat = pickNutrient(nuts, 'fat', selectedFood.fat);
        selectedFood.fiber = pickNutrient(nuts, 'fiber', selectedFood.fiber);
        selectedFood.sugar = pickNutrient(nuts, 'sugars', selectedFood.sugar);
        selectedFood.sodium = pickNutrient(nuts, 'sodium', selectedFood.sodium);
        selectedFood.saturatedFat = pickNutrient(nuts, 'saturated_fat', selectedFood.saturatedFat);
        selectedFood.cholesterol = pickNutrient(nuts, 'cholesterol', selectedFood.cholesterol);
        selectedFood.potassium = pickNutrient(nuts, 'potassium', selectedFood.potassium);
        if (detail.portions && detail.portions.length) {
            selectedFood.servings = detail.portions.map(function (p) {
                return { desc: p.desc, size: p.grams || 100 };
            });
        }
    }

    function finishServingUI() {
        if (!selectedFood || !els.servingSelect) {
            return;
        }
        els.servingSelect.innerHTML = selectedFood.servings.map(function (s, i) {
            return '<option value="' + i + '">' + escHtml(s.desc) + '</option>';
        }).join('');
        if (els.selectedName) {
            els.selectedName.textContent = selectedFood.name;
        }
        if (els.selectedInfo) {
            els.selectedInfo.innerHTML =
                pill('cal', r2(selectedFood.cal) + ' kcal') +
                pill('pro', r2(selectedFood.pro) + 'g P') +
                pill('carb', r2(selectedFood.carb) + 'g C') +
                pill('fat', r2(selectedFood.fat) + 'g F') +
                '<span class="tool-pill note">per 100g</span>';
        }
        if (els.qtyInput) {
            els.qtyInput.value = '1';
        }
        if (els.addBtn) {
            els.addBtn.disabled = false;
        }
        hideEl(els.detailPanel);
        updateServingPreview();
        showAddPanel(true);
    }

    function getServingFactor() {
        if (!selectedFood) {
            return 0;
        }
        var qty = parseFloat(els.qtyInput && els.qtyInput.value) || 1;
        var idx = parseInt(els.servingSelect && els.servingSelect.value, 10) || 0;
        var srv = selectedFood.servings[idx] || { size: 100 };
        return (qty * srv.size) / 100;
    }

    function updateServingPreview() {
        if (!selectedFood || !els.previewCal) {
            return;
        }
        var factor = getServingFactor();
        var cal = Math.round(selectedFood.cal * factor);
        els.previewCal.textContent = cal + ' kcal';
    }

    function addFood() {
        if (!selectedFood) {
            return;
        }
        var factor = getServingFactor();
        var srvIdx = parseInt(els.servingSelect.value, 10) || 0;
        var srvText = els.servingSelect.options[els.servingSelect.selectedIndex].text;
        var qty = parseFloat(els.qtyInput.value) || 1;

        mealItems.push({
            id: Date.now() + Math.floor(Math.random() * 1000),
            name: selectedFood.name,
            cal: selectedFood.cal * factor,
            pro: selectedFood.pro * factor,
            carb: selectedFood.carb * factor,
            fat: selectedFood.fat * factor,
            fiber: selectedFood.fiber * factor,
            sugar: selectedFood.sugar * factor,
            sodium: selectedFood.sodium * factor,
            satfat: selectedFood.saturatedFat * factor,
            chol: selectedFood.cholesterol * factor,
            potassium: selectedFood.potassium * factor,
            qty: qty,
            serving: srvText
        });

        updateUI();
        setFlowStep(3);
        showToast('Added to your meal');
        hideAddPanel();
        hideEl(els.detailPanel);
        hideEl(els.error);
        if (els.resultsBox && searchResults.length) {
            showEl(els.resultsBox);
        }
        setTimeout(function () { setFlowStep(1); }, 1200);
        selectedFood = null;
    }

    function cancelAddSelection() {
        selectedFood = null;
        detailRequestId++;
        hideAddPanel();
        if (els.resultsBox) {
            els.resultsBox.querySelectorAll('.tool-result').forEach(function (node) {
                node.classList.remove('selected');
            });
            if (searchResults.length) {
                showEl(els.resultsBox);
            }
        }
        setFlowStep(1);
    }

    function showAddPanel(show) {
        if (!els.servingArea) return;
        if (show) {
            els.servingArea.classList.remove('tool-hidden');
        } else {
            els.servingArea.classList.add('tool-hidden');
        }
        if (els.emptyState && mealItems.length === 0) {
            els.emptyState.classList.toggle('tool-hidden', show);
        }
    }

    function hideAddPanel() {
        showAddPanel(false);
    }

    function resetSelectionUI() {
        hideAddPanel();
        hideEl(els.detailPanel);
        hideEl(els.error);
        detailRequestId++;
    }

    function setGoal() {
        var v = parseInt(els.goalInput && els.goalInput.value, 10);
        if (v >= 500 && v <= 10000) {
            dailyGoal = v;
            saveState();
            updateUI();
            showToast('Daily goal set to ' + v + ' kcal');
        } else {
            showToast('Enter a goal between 500 and 10,000 kcal');
        }
    }

    function updateUI() {
        saveState();
        if (!els.tableBody) {
            return;
        }

        els.tableBody.innerHTML = '';
        mealItems.forEach(function (item) {
            var tr = document.createElement('tr');
            tr.innerHTML =
                '<td><strong>' + escHtml(item.name) + '</strong><br>' +
                '<small class="tool-serving-label">' + escHtml(item.serving) + ' × ' + item.qty + '</small></td>' +
                '<td class="tool-tc"><strong>' + Math.round(item.cal) + '</strong></td>' +
                '<td class="tool-tc">' + item.pro.toFixed(1) + 'g</td>' +
                '<td class="tool-tc">' + item.carb.toFixed(1) + 'g</td>' +
                '<td class="tool-tc">' + item.fat.toFixed(1) + 'g</td>' +
                '<td class="tool-tc"><button type="button" class="tool-remove-btn" data-id="' + item.id +
                '" aria-label="Remove ' + escHtml(item.name) + '">&times;</button></td>';
            els.tableBody.appendChild(tr);
        });

        els.tableBody.querySelectorAll('.tool-remove-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.getAttribute('data-id'), 10);
                mealItems = mealItems.filter(function (m) { return m.id !== id; });
                updateUI();
                showToast('Item removed');
            });
        });

        var has = mealItems.length > 0;
        toggleMealVisibility(has);

        if (els.itemCount) {
            els.itemCount.textContent = String(mealItems.length);
        }

        var t = { cal: 0, pro: 0, carb: 0, fat: 0, fiber: 0, sugar: 0, sodium: 0, satfat: 0, chol: 0, potassium: 0 };
        mealItems.forEach(function (m) {
            t.cal += m.cal;
            t.pro += m.pro;
            t.carb += m.carb;
            t.fat += m.fat;
            t.fiber += m.fiber;
            t.sugar += m.sugar;
            t.sodium += m.sodium;
            t.satfat += m.satfat || 0;
            t.chol += m.chol || 0;
            t.potassium += m.potassium || 0;
        });

        setText(els.totalCal, Math.round(t.cal).toString());
        setText(els.totalPro, t.pro.toFixed(1));
        setText(els.totalCarb, t.carb.toFixed(1));
        setText(els.totalFat, t.fat.toFixed(1));
        setText(els.totalFiber, t.fiber.toFixed(1) + 'g');
        setText(els.totalSugar, t.sugar.toFixed(1) + 'g');
        setText(els.totalSodium, Math.round(t.sodium) + 'mg');
        setText(els.totalSatFat, t.satfat.toFixed(1) + 'g');
        setText(els.totalCholesterol, Math.round(t.chol) + 'mg');
        setText(els.totalPotassium, Math.round(t.potassium) + 'mg');

        if (els.tableFoot) {
            els.tableFoot.innerHTML = has
                ? '<tr class="tool-totals-row">' +
                '<td><strong>Meal total</strong></td>' +
                '<td class="tool-tc"><strong>' + Math.round(t.cal) + '</strong></td>' +
                '<td class="tool-tc"><strong>' + t.pro.toFixed(1) + 'g</strong></td>' +
                '<td class="tool-tc"><strong>' + t.carb.toFixed(1) + 'g</strong></td>' +
                '<td class="tool-tc"><strong>' + t.fat.toFixed(1) + 'g</strong></td>' +
                '<td class="tool-tc"></td></tr>'
                : '';
        }

        var macroSum = t.pro + t.carb + t.fat;
        var pp = macroSum ? (t.pro / macroSum) * 100 : 0;
        var cp = macroSum ? (t.carb / macroSum) * 100 : 0;
        var fp = macroSum ? (t.fat / macroSum) * 100 : 0;

        if (els.proSeg) els.proSeg.style.width = pp + '%';
        if (els.carbSeg) els.carbSeg.style.width = cp + '%';
        if (els.fatSeg) els.fatSeg.style.width = fp + '%';
        setText(els.proPct, pp.toFixed(0) + '%');
        setText(els.carbPct, cp.toFixed(0) + '%');
        setText(els.fatPct, fp.toFixed(0) + '%');

        var gp = dailyGoal > 0 ? (t.cal / dailyGoal) * 100 : 0;
        if (els.goalBar) {
            els.goalBar.style.width = Math.min(gp, 100) + '%';
            els.goalBar.classList.toggle('is-over', gp > 100);
        }
        setText(els.goalPct, gp.toFixed(0) + '%');
        setText(els.goalEaten, Math.round(t.cal) + ' kcal in this meal');
        setText(els.goalDisplay, 'Goal ' + dailyGoal);
        if (els.goalInput && !els.goalInput.value) {
            els.goalInput.placeholder = String(dailyGoal);
        }
    }

    function toggleMealVisibility(hasItems) {
        if (els.emptyState) {
            els.emptyState.classList.toggle('tool-hidden', hasItems);
        }
        if (els.tableWrap) {
            els.tableWrap.classList.toggle('is-visible', hasItems);
        }
        if (els.clearBtn) {
            els.clearBtn.classList.toggle('is-visible', hasItems);
        }
    }

    function parseServingG(servingText) {
        if (!servingText) return 100;
        var m = /([\d]+(?:[.,]\d+)?)\s*g\b/i.exec(String(servingText));
        if (!m) return 100;
        var v = parseFloat(String(m[1]).replace(',', '.'));
        return isNaN(v) ? 100 : v;
    }

    function setStatus(msg) {
        if (els.sourceInfo) {
            els.sourceInfo.textContent = msg || '';
        }
    }

    function showEl(el) {
        if (el) el.classList.remove('tool-hidden');
    }

    function hideEl(el) {
        if (el) el.classList.add('tool-hidden');
    }

    function setText(el, t) {
        if (el) el.textContent = t;
    }

    function r2(v) {
        return Math.round((v || 0) * 10) / 10;
    }

    function showError(msg) {
        if (els.error) {
            els.error.textContent = msg;
            showEl(els.error);
        }
        setStatus('');
    }

    function escHtml(s) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s || ''));
        return d.innerHTML;
    }

    function showToast(msg) {
        var t = document.createElement('div');
        t.className = 'tool-toast';
        t.setAttribute('role', 'status');
        t.textContent = msg;
        document.body.appendChild(t);
        requestAnimationFrame(function () {
            t.classList.add('show');
        });
        setTimeout(function () {
            t.classList.remove('show');
            setTimeout(function () { t.remove(); }, 300);
        }, 2600);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
