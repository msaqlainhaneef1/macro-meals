function initNutritionSearch(foodDB){var input=document.getElementById('food-search');var resultsEl=document.getElementById('search-results');var detailEl=document.getElementById('food-detail');var trackerEl=document.getElementById('meal-tracker-body');var totalEl=document.getElementById('meal-tracker-totals');var progressEl=document.getElementById('cal-progress');var goalText=document.getElementById('goal-text');var barcodeInput=document.getElementById('barcode-input');var barcodeBtn=document.getElementById('barcode-search-btn');var compareEl=document.getElementById('compare-panel');var goalInput=document.getElementById('daily-goal-input');if(!input)return;var trackedMeals=[];var dailyGoal=2000;var searchTimeout=null;var compareItems=[];var servingMultiplier=1;try{var saved=localStorage.getItem('nc_meals');if(saved)trackedMeals=JSON.parse(saved);var savedGoal=localStorage.getItem('nc_goal');if(savedGoal)dailyGoal=parseInt(savedGoal);}catch(e){}
if(goalInput){goalInput.value=dailyGoal;goalInput.addEventListener('change',function(){dailyGoal=parseInt(this.value)||2000;try{localStorage.setItem('nc_goal',dailyGoal);}catch(e){}
renderTracker();});}
var DV={fat:78,saturated_fat:20,cholesterol:300,sodium:2300,carbs:275,fiber:28,sugars:50,protein:50,vitamin_a:900,vitamin_c:90,vitamin_d:20,vitamin_e:15,vitamin_k:120,calcium:1300,iron:18,potassium:4700,thiamin:1.2,riboflavin:1.3,niacin:16,vitamin_b6:1.7,folate:400,vitamin_b12:2.4,magnesium:420,zinc:11,selenium:55,copper:0.9,manganese:2.3,phosphorus:1250};function dvPct(val,key){if(!val||!DV[key])return null;return Math.round((val/DV[key])*100);}
input.addEventListener('input',function(){var q=input.value.trim();if(q.length<2){resultsEl.classList.remove('show');return;}
var localMatches=[];if(foodDB&&foodDB.length){localMatches=foodDB.filter(function(f){return f.name.toLowerCase().indexOf(q.toLowerCase())>-1;}).slice(0,5).map(function(f){return{id:'local_'+f.name,name:f.name,nutrients:{calories:f.calories,protein:f.protein,carbs:f.carbs,fat:f.fat,fiber:f.fiber},serving:f.serving||'100g',source:'Local Database',sourceIcon:'local'};});}
if(localMatches.length>0)showResults(localMatches);clearTimeout(searchTimeout);searchTimeout=setTimeout(function(){fetchFromAPI(q,localMatches);},350);});function fetchFromAPI(query,localMatches){var isBarcode=/^\d{8,14}$/.test(query);var url='/api/food.php?'+(isBarcode?'barcode=':'query=')+encodeURIComponent(query);var indicator=document.getElementById('search-loading');if(indicator)indicator.style.display='';fetch(url).then(function(res){return res.json();}).then(function(data){if(indicator)indicator.style.display='none';if(!data.success)return;var apiItems=[];if(data.type==='search'&&Array.isArray(data.data)){apiItems=data.data;}else if(data.type==='barcode'&&data.data){apiItems=[data.data];}
var combined=localMatches.slice();var names={};combined.forEach(function(m){names[m.name.toLowerCase()]=true;});apiItems.forEach(function(item){var key=(item.name||'').toLowerCase();if(!names[key]){combined.push(item);names[key]=true;}});showResults(combined);}).catch(function(){if(indicator)indicator.style.display='none';});}
if(barcodeInput&&barcodeBtn){barcodeBtn.addEventListener('click',function(){var code=barcodeInput.value.trim();if(!code)return;searchBarcode(code);});barcodeInput.addEventListener('keypress',function(e){if(e.key==='Enter'){var code=barcodeInput.value.trim();if(code)searchBarcode(code);}});}
function searchBarcode(code){var indicator=document.getElementById('search-loading');if(indicator)indicator.style.display='';fetch('/api/food.php?barcode='+encodeURIComponent(code)).then(function(res){return res.json();}).then(function(data){if(indicator)indicator.style.display='none';if(data.success&&data.data){showDetail(data.data);resultsEl.classList.remove('show');}else{detailEl.innerHTML='<div class="search-error"><span class="error-icon">&#9888;</span> No product found for barcode: '+code+'</div>';detailEl.classList.add('show');}}).catch(function(){if(indicator)indicator.style.display='none';});}
function showResults(matches){if(matches.length===0){resultsEl.classList.remove('show');return;}
resultsEl.innerHTML='';matches.forEach(function(item){var div=document.createElement('div');div.className='search-result-item';var cal=item.nutrients?item.nutrients.calories:item.calories;var sourceTag='<span class="source-badge source-'+
(item.sourceIcon||'usda')+'">'+
(item.source==='Open Food Facts'?'OFF':item.source==='Local Database'?'Local':'USDA')+'</span>';var brandTag=item.brand?'<span class="result-brand">'+item.brand+'</span>':'';div.innerHTML='<div class="result-left"><span class="result-name">'+
(item.name||'Unknown')+'</span>'+brandTag+'</div>'+
'<div class="result-right">'+
(cal?'<span class="result-cal">'+Math.round(cal)+' kcal</span>':'')+
sourceTag+'</div>';div.addEventListener('click',function(){showDetail(item);resultsEl.classList.remove('show');input.value=item.name||'';});resultsEl.appendChild(div);});resultsEl.classList.add('show');}
document.addEventListener('click',function(e){if(!e.target.closest('.search-card'))resultsEl.classList.remove('show');});function showDetail(food){var n=food.nutrients||food;servingMultiplier=1;detailEl.classList.add('show');var headerHTML='<div class="detail-header">'+
'<h4>'+esc(food.name||'Unknown Food')+
(food.source?' <span class="detail-source source-badge source-'+(food.sourceIcon||'usda')+'">'+
(food.source==='Open Food Facts'?'Open Food Facts':'USDA')+'</span>':'')+
'</h4>'+
(food.brand?'<div class="detail-brand">&#127970; '+esc(food.brand)+'</div>':'')+
(food.category?'<div class="detail-category">&#128193; '+esc(food.category)+'</div>':'')+
'</div>';var badgesHTML='';if(food.nutriscore||food.nova){badgesHTML='<div class="detail-badges">';if(food.nutriscore&&food.nutriscore!=='unknown'&&food.nutriscore!=='not-applicable'){badgesHTML+='<div class="nutriscore-badge ns-'+food.nutriscore+'">Nutri-Score '+food.nutriscore.toUpperCase()+'</div>';}
if(food.nova){var novaLabels={1:'Unprocessed',2:'Processed ingredients',3:'Processed',4:'Ultra-processed'};badgesHTML+='<div class="nova-badge nova-'+food.nova+'">NOVA '+food.nova+(novaLabels[food.nova]?' &mdash; '+novaLabels[food.nova]:'')+'</div>';}
badgesHTML+='</div>';}
var imageHTML=food.image?'<div class="detail-image"><img src="'+food.image+'" alt="'+esc(food.name)+'" loading="lazy"></div>':'';var servingHTML='<div class="serving-adjuster">'+
'<label>Serving:</label>'+
'<div class="serving-controls">'+
'<button class="serving-btn" data-mult="0.5">&#189;</button>'+
'<button class="serving-btn active" data-mult="1">1x</button>'+
'<button class="serving-btn" data-mult="1.5">1.5x</button>'+
'<button class="serving-btn" data-mult="2">2x</button>'+
'<input type="number" id="custom-serving" value="1" min="0.1" max="10" step="0.1" class="custom-serving">'+
'</div>'+
'<span class="serving-size">per '+(food.serving||'100g')+'</span>'+
'</div>';var pillsHTML=buildMacroPills(n,1);var barsHTML=buildMacroBars(n,1);var labelHTML=buildNutritionLabel(food,n,1);var vmHTML=buildVitaminMineralGrid(n,1);var allergenHTML='';if(food.allergens&&food.allergens.length>0){allergenHTML='<div class="allergen-section"><h5>&#9888; Allergens</h5><div class="allergen-tags">';food.allergens.forEach(function(a){allergenHTML+='<span class="allergen-tag">'+esc(a)+'</span>';});allergenHTML+='</div></div>';}
var ingredientHTML='';if(food.ingredients){ingredientHTML='<div class="ingredients-section"><h5>&#128220; Ingredients</h5>'+
'<p class="ingredients-text">'+esc(food.ingredients)+'</p></div>';}
var actionsHTML='<div class="detail-actions">'+
'<button class="btn btn-primary" id="add-food-btn" style="flex:1">&#10133; Add to Meal Tracker</button>'+
'<button class="btn btn-outline-compare" id="compare-food-btn">&#9878; Compare</button>'+
'</div>';detailEl.innerHTML='<div class="food-detail-card">'+
headerHTML+badgesHTML+imageHTML+servingHTML+
'<div id="macro-pills">'+pillsHTML+'</div>'+
'<div id="macro-bars">'+barsHTML+'</div>'+
'<div id="nutrition-label">'+labelHTML+'</div>'+
'<div id="vitamin-minerals">'+vmHTML+'</div>'+
allergenHTML+ingredientHTML+actionsHTML+
'</div>';detailEl.querySelectorAll('.serving-btn').forEach(function(btn){btn.addEventListener('click',function(){detailEl.querySelectorAll('.serving-btn').forEach(function(b){b.classList.remove('active');});btn.classList.add('active');servingMultiplier=parseFloat(btn.getAttribute('data-mult'));var csi=document.getElementById('custom-serving');if(csi)csi.value=servingMultiplier;updateServingDisplay(n,food);});});var customServing=document.getElementById('custom-serving');if(customServing){customServing.addEventListener('input',function(){servingMultiplier=parseFloat(this.value)||1;detailEl.querySelectorAll('.serving-btn').forEach(function(b){b.classList.remove('active');});updateServingDisplay(n,food);});}
document.getElementById('add-food-btn').addEventListener('click',function(){var m=servingMultiplier;trackedMeals.push({name:food.name,qty:m,serving:food.serving||'100g',calories:r(n.calories,m),protein:r(n.protein,m),carbs:r(n.carbs,m),fat:r(n.fat,m),fiber:r(n.fiber,m),sugars:r(n.sugars,m),sodium:r(n.sodium,m),source:food.source||''});saveMeals();renderTracker();showToast(food.name+' added to tracker!');});document.getElementById('compare-food-btn').addEventListener('click',function(){if(compareItems.length>=3){showToast('Max 3 items for comparison');return;}
compareItems.push({name:food.name,nutrients:n,serving:food.serving||'100g'});renderCompare();showToast(food.name+' added to comparison');});}
function r(val,mult){return Math.round((val||0)*mult*10)/10;}
function updateServingDisplay(n,food){var m=servingMultiplier;var pe=document.getElementById('macro-pills');if(pe)pe.innerHTML=buildMacroPills(n,m);var be=document.getElementById('macro-bars');if(be)be.innerHTML=buildMacroBars(n,m);var le=document.getElementById('nutrition-label');if(le)le.innerHTML=buildNutritionLabel(food,n,m);var ve=document.getElementById('vitamin-minerals');if(ve)ve.innerHTML=buildVitaminMineralGrid(n,m);}
function buildMacroPills(n,m){var fields=[{key:'calories',label:'Calories',unit:'',cls:'pill-cal'},{key:'protein',label:'Protein',unit:'g',cls:'pill-pro'},{key:'carbs',label:'Carbs',unit:'g',cls:'pill-carb'},{key:'fat',label:'Fat',unit:'g',cls:'pill-fat'},{key:'fiber',label:'Fiber',unit:'g',cls:'pill-fib'},{key:'sugars',label:'Sugars',unit:'g',cls:'pill-sug'},{key:'sodium',label:'Sodium',unit:'mg',cls:'pill-sod'},{key:'cholesterol',label:'Cholesterol',unit:'mg',cls:'pill-chol'}];var html='<div class="nutrition-pills">';fields.forEach(function(f){var v=n[f.key];if(v===null||v===undefined)return;html+='<div class="nutrition-pill '+f.cls+'">'+
'<div class="val">'+r(v,m)+f.unit+'</div>'+
'<div class="lbl">'+f.label+'</div></div>';});html+='</div>';return html;}
function buildMacroBars(n,m){var cal=r(n.calories,m)||1;var pro=r(n.protein,m)||0;var carb=r(n.carbs,m)||0;var fat=r(n.fat,m)||0;var proCal=pro*4,carbCal=carb*4,fatCal=fat*9;var total=proCal+carbCal+fatCal||1;var proPct=Math.round(proCal/total*100);var carbPct=Math.round(carbCal/total*100);var fatPct=100-proPct-carbPct;return'<div class="macro-bars">'+
'<div class="macro-bar-stacked">'+
'<div class="stacked-segment protein" style="width:'+proPct+'%"></div>'+
'<div class="stacked-segment carbs" style="width:'+carbPct+'%"></div>'+
'<div class="stacked-segment fat" style="width:'+fatPct+'%"></div>'+
'</div>'+
'<div class="macro-bar-legend">'+
'<span class="legend-item"><span class="legend-dot protein"></span>Protein '+proPct+'%</span>'+
'<span class="legend-item"><span class="legend-dot carbs"></span>Carbs '+carbPct+'%</span>'+
'<span class="legend-item"><span class="legend-dot fat"></span>Fat '+fatPct+'%</span>'+
'</div></div>';}
function buildNutritionLabel(food,n,m){function dv(val,ref){if(!val||!ref)return'';return Math.round((r(val,m)/ref)*100)+'%';}
return'<div class="nf-label">'+
'<div class="nf-title">Nutrition Facts</div>'+
(food.serving?'<div class="nf-serving">Serving Size '+(m!==1?m+'x ':'')+esc(food.serving||'100g')+'</div>':'')+
'<div class="nf-divider-thick"></div>'+
'<div class="nf-cal-row"><span class="nf-cal-label">Calories</span><span class="nf-cal-val">'+r(n.calories,m)+'</span></div>'+
'<div class="nf-divider-medium"></div>'+
'<div class="nf-dv-header">% Daily Value*</div>'+
'<div class="nf-divider-thin"></div>'+
nfRow('Total Fat',r(n.fat,m),'g',dv(n.fat,DV.fat),true)+
(n.saturated_fat?nfRow('Saturated Fat',r(n.saturated_fat,m),'g',dv(n.saturated_fat,DV.saturated_fat),false,true):'')+
(n.trans_fat!==null&&n.trans_fat!==undefined?nfRow('Trans Fat',r(n.trans_fat,m),'g','',false,true):'')+
(n.cholesterol?nfRow('Cholesterol',r(n.cholesterol,m),'mg',dv(n.cholesterol,DV.cholesterol),true):'')+
nfRow('Sodium',r(n.sodium,m),'mg',dv(n.sodium,DV.sodium),true)+
nfRow('Total Carbohydrate',r(n.carbs,m),'g',dv(n.carbs,DV.carbs),true)+
(n.fiber?nfRow('Dietary Fiber',r(n.fiber,m),'g',dv(n.fiber,DV.fiber),false,true):'')+
(n.sugars?nfRow('Total Sugars',r(n.sugars,m),'g',dv(n.sugars,DV.sugars),false,true):'')+
nfRow('Protein',r(n.protein,m),'g',dv(n.protein,DV.protein),true)+
'<div class="nf-divider-thick"></div>'+
nfMicroRow('Vitamin D',r(n.vitamin_d,m),'mcg',dv(n.vitamin_d,DV.vitamin_d))+
nfMicroRow('Calcium',r(n.calcium,m),'mg',dv(n.calcium,DV.calcium))+
nfMicroRow('Iron',r(n.iron,m),'mg',dv(n.iron,DV.iron))+
nfMicroRow('Potassium',r(n.potassium,m),'mg',dv(n.potassium,DV.potassium))+
'<div class="nf-footnote">* The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.</div>'+
'</div>';}
function nfRow(label,val,unit,dvPctStr,bold,indent){return'<div class="nf-divider-thin"></div>'+
'<div class="nf-row'+(indent?' nf-indent':'')+'">'+
'<span>'+(bold?'<strong>':'')+label+(bold?'</strong>':'')+' '+(val||0)+unit+'</span>'+
'<span>'+(dvPctStr||'')+'</span></div>';}
function nfMicroRow(label,val,unit,dvPctStr){if(!val)return'';return'<div class="nf-divider-thin"></div>'+
'<div class="nf-row"><span>'+label+' '+val+unit+'</span><span>'+(dvPctStr||'')+'</span></div>';}
function buildVitaminMineralGrid(n,m){var items=[{key:'vitamin_a',label:'Vitamin A',unit:'mcg'},{key:'vitamin_c',label:'Vitamin C',unit:'mg'},{key:'vitamin_d',label:'Vitamin D',unit:'mcg'},{key:'vitamin_e',label:'Vitamin E',unit:'mg'},{key:'vitamin_k',label:'Vitamin K',unit:'mcg'},{key:'thiamin',label:'Thiamin (B1)',unit:'mg'},{key:'riboflavin',label:'Riboflavin (B2)',unit:'mg'},{key:'niacin',label:'Niacin (B3)',unit:'mg'},{key:'vitamin_b6',label:'Vitamin B6',unit:'mg'},{key:'folate',label:'Folate',unit:'mcg'},{key:'vitamin_b12',label:'Vitamin B12',unit:'mcg'},{key:'calcium',label:'Calcium',unit:'mg'},{key:'iron',label:'Iron',unit:'mg'},{key:'magnesium',label:'Magnesium',unit:'mg'},{key:'phosphorus',label:'Phosphorus',unit:'mg'},{key:'potassium',label:'Potassium',unit:'mg'},{key:'zinc',label:'Zinc',unit:'mg'},{key:'copper',label:'Copper',unit:'mg'},{key:'manganese',label:'Manganese',unit:'mg'},{key:'selenium',label:'Selenium',unit:'mcg'}];var hasAny=false;items.forEach(function(it){if(n[it.key])hasAny=true;});if(!hasAny)return'';var html='<div class="vm-section"><h5>&#128138; Vitamins & Minerals</h5><div class="vm-grid">';items.forEach(function(it){var v=n[it.key];if(!v)return;var pct=dvPct(r(v,m),it.key);var cls=pct>=100?'vm-high':pct>=50?'vm-good':pct>=20?'vm-moderate':'vm-low';html+='<div class="vm-item '+cls+'">'+
'<div class="vm-name">'+it.label+'</div>'+
'<div class="vm-val">'+r(v,m)+it.unit+'</div>'+
(pct!==null?'<div class="vm-pct">'+pct+'% DV</div>':'')+
'</div>';});html+='</div></div>';return html;}
function renderCompare(){if(!compareEl)return;if(compareItems.length===0){compareEl.style.display='none';return;}
compareEl.style.display='';var fields=['calories','protein','carbs','fat','fiber','sugars','sodium','cholesterol','saturated_fat'];var units={calories:'',protein:'g',carbs:'g',fat:'g',fiber:'g',sugars:'g',sodium:'mg',cholesterol:'mg',saturated_fat:'g'};var html='<div class="compare-card"><h4>&#9878; Food Comparison <button class="reset-compare" id="reset-compare">&times; Clear</button></h4>';html+='<div class="compare-table-wrap"><table class="compare-table"><thead><tr><th>Nutrient</th>';compareItems.forEach(function(item){html+='<th>'+esc(item.name)+'<br><small>per '+esc(item.serving)+'</small></th>';});html+='</tr></thead><tbody>';fields.forEach(function(f){html+='<tr><td class="compare-nutrient">'+f.charAt(0).toUpperCase()+f.slice(1).replace('_',' ')+'</td>';var vals=compareItems.map(function(item){return item.nutrients[f]||0;});var maxV=Math.max.apply(null,vals);compareItems.forEach(function(item,i){var v=item.nutrients[f]||0;var cls=v===maxV&&compareItems.length>1?' compare-highlight':'';html+='<td class="'+cls+'">'+v+(units[f]||'')+'</td>';});html+='</tr>';});html+='</tbody></table></div></div>';compareEl.innerHTML=html;document.getElementById('reset-compare').addEventListener('click',function(){compareItems=[];renderCompare();});}
function renderTracker(){var totals={calories:0,protein:0,carbs:0,fat:0,fiber:0,sugars:0,sodium:0};trackedMeals.forEach(function(m){totals.calories+=m.calories||0;totals.protein+=m.protein||0;totals.carbs+=m.carbs||0;totals.fat+=m.fat||0;totals.fiber+=m.fiber||0;totals.sugars+=m.sugars||0;totals.sodium+=m.sodium||0;});if(trackerEl){trackerEl.innerHTML='';if(trackedMeals.length===0){trackerEl.innerHTML='<tr><td colspan="6" style="text-align:center;color:var(--text-light);padding:1.5rem;font-style:italic">No foods tracked yet. Search above to add foods.</td></tr>';}else{trackedMeals.forEach(function(m,i){trackerEl.innerHTML+='<tr>'+
'<td><span class="tracker-food-name">'+esc(m.name)+(m.qty>1?' <small>(x'+m.qty+')</small>':'')+'</span></td>'+
'<td class="tracker-num">'+Math.round(m.calories)+'</td>'+
'<td class="tracker-num">'+(m.protein||0).toFixed(1)+'g</td>'+
'<td class="tracker-num">'+(m.carbs||0).toFixed(1)+'g</td>'+
'<td class="tracker-num">'+(m.fat||0).toFixed(1)+'g</td>'+
'<td><button class="remove-food-btn" data-idx="'+i+'" title="Remove">&#10005;</button></td></tr>';});}
trackerEl.querySelectorAll('.remove-food-btn').forEach(function(btn){btn.addEventListener('click',function(){trackedMeals.splice(parseInt(btn.getAttribute('data-idx')),1);saveMeals();renderTracker();});});}
if(totalEl){totalEl.innerHTML='<td><strong>Total</strong></td>'+
'<td><strong>'+Math.round(totals.calories)+'</strong></td>'+
'<td><strong>'+totals.protein.toFixed(1)+'g</strong></td>'+
'<td><strong>'+totals.carbs.toFixed(1)+'g</strong></td>'+
'<td><strong>'+totals.fat.toFixed(1)+'g</strong></td><td></td>';}
if(progressEl){var pct=Math.min(100,Math.round(totals.calories/dailyGoal*100));progressEl.style.width=pct+'%';progressEl.className='progress-fill'+(pct>=100?' progress-over':pct>=80?' progress-warn':'');}
if(goalText){goalText.innerHTML='<span>'+Math.round(totals.calories)+' consumed</span><span>'+dailyGoal+' goal</span>';}
var macroSumEl=document.getElementById('tracker-macro-summary');if(macroSumEl){macroSumEl.innerHTML='<div class="tracker-macro pill-pro"><span class="tm-val">'+totals.protein.toFixed(1)+'g</span><span class="tm-lbl">Protein</span></div>'+
'<div class="tracker-macro pill-carb"><span class="tm-val">'+totals.carbs.toFixed(1)+'g</span><span class="tm-lbl">Carbs</span></div>'+
'<div class="tracker-macro pill-fat"><span class="tm-val">'+totals.fat.toFixed(1)+'g</span><span class="tm-lbl">Fat</span></div>'+
'<div class="tracker-macro pill-fib"><span class="tm-val">'+totals.fiber.toFixed(1)+'g</span><span class="tm-lbl">Fiber</span></div>';}}
function saveMeals(){try{localStorage.setItem('nc_meals',JSON.stringify(trackedMeals));}catch(e){}}
var clearBtn=document.getElementById('clear-tracker-btn');if(clearBtn){clearBtn.addEventListener('click',function(){trackedMeals=[];saveMeals();renderTracker();showToast('Meal tracker cleared');});}
function showToast(msg){var t=document.createElement('div');t.className='toast-notification';t.textContent=msg;document.body.appendChild(t);setTimeout(function(){t.classList.add('show');},10);setTimeout(function(){t.classList.remove('show');setTimeout(function(){t.remove();},300);},2500);}
function esc(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
renderTracker();renderCompare();}