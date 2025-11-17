MERGE (i:Ingredient {ingredient_id: 'ing_acai_juice'})
SET i.canonical_name = 'acai juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["acai juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_achiote_paste'})
SET i.canonical_name = 'achiote paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["achiote pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_achiote_powder'})
SET i.canonical_name = 'achiote powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["achiote powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_adobo_sauce'})
SET i.canonical_name = 'adobo sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["adobo sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_adzuki_bean'})
SET i.canonical_name = 'adzuki bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["adzuki beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_agar_agar_flak'})
SET i.canonical_name = 'agar agar flak',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["agar agar flaks", "agaragarflak", "agaragarflaks"],
    i.variations = '{"other": ["agar agar flak"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ahi_tuna_steak'})
SET i.canonical_name = 'ahi tuna steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["ahi tuna steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_alaskan_king_crab_leg'})
SET i.canonical_name = 'alaskan king crab leg',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["alaskan king crab legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_alaskan_king_salmon'})
SET i.canonical_name = 'alaskan king salmon',
    i.category = 'seafood',
    i.base = 'salmon',
    i.alt_names = ["alaskan king salmons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ale'})
SET i.canonical_name = 'ale',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["ales"],
    i.variations = '{"other": ["ale"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_aleppo_pepper'})
SET i.canonical_name = 'aleppo pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["aleppo peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_alfalfa_sprout'})
SET i.canonical_name = 'alfalfa sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["alfalfa sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_alfredo_sauce'})
SET i.canonical_name = 'alfredo sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["alfredo sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_alfredostyle_pasta_sauce'})
SET i.canonical_name = 'alfredostyle pasta sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["alfredostyle pasta sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_all_beef_hot_dog'})
SET i.canonical_name = 'all beef hot dog',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["all beef hot dogs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_all_potato_purpo'})
SET i.canonical_name = 'all potato purpo',
    i.category = 'vegetable',
    i.base = 'potato',
    i.alt_names = ["all potato purpos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_allspice_berry'})
SET i.canonical_name = 'allspice berry',
    i.category = 'fruit',
    i.base = 'berry',
    i.alt_names = ["allspice berries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond'})
SET i.canonical_name = 'almond',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["almonds"],
    i.variations = '{"other": ["almond", "raw almond"], "cut_or_form": ["smoked almond", "whole almond"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_almond_butter'})
SET i.canonical_name = 'almond butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["almond butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_flour'})
SET i.canonical_name = 'almond flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["almond flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_liqueur'})
SET i.canonical_name = 'almond liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["almond liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_meal'})
SET i.canonical_name = 'almond meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["almond meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_milk'})
SET i.canonical_name = 'almond milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["almond milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_oil'})
SET i.canonical_name = 'almond oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["almond oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_paste'})
SET i.canonical_name = 'almond paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["almond pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_almond_syrup'})
SET i.canonical_name = 'almond syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["almond syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_aloe_juice'})
SET i.canonical_name = 'aloe juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["aloe juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_alphabet_pasta'})
SET i.canonical_name = 'alphabet pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["alphabet pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_amaranth'})
SET i.canonical_name = 'amaranth',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["amaranths"],
    i.variations = '{"other": ["amaranth"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_amarena_cherry'})
SET i.canonical_name = 'amarena cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["amarena cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_amaretto_liqueur'})
SET i.canonical_name = 'amaretto liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["amaretto liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anasazi_bean'})
SET i.canonical_name = 'anasazi bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["anasazi beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ancho_powder'})
SET i.canonical_name = 'ancho powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["ancho powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anchovy'})
SET i.canonical_name = 'anchovy',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["anchovies"],
    i.variations = '{"other": ["anchovy"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_anchovy_filet'})
SET i.canonical_name = 'anchovy filet',
    i.category = 'seafood',
    i.base = 'anchovy',
    i.alt_names = ["anchovy filets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anchovy_fillet'})
SET i.canonical_name = 'anchovy fillet',
    i.category = 'seafood',
    i.base = 'anchovy',
    i.alt_names = ["anchovy fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anchovy_paste'})
SET i.canonical_name = 'anchovy paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["anchovy pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anise_liqueur'})
SET i.canonical_name = 'anise liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["anise liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anise_oil'})
SET i.canonical_name = 'anise oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["anise oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anise_powder'})
SET i.canonical_name = 'anise powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["anise powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_anjou_pear'})
SET i.canonical_name = 'anjou pear',
    i.category = 'fruit',
    i.base = 'pear',
    i.alt_names = ["anjou pears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_annatto_oil'})
SET i.canonical_name = 'annatto oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["annatto oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_annatto_powder'})
SET i.canonical_name = 'annatto powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["annatto powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple'})
SET i.canonical_name = 'apple',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["apples"],
    i.variations = '{"other": ["apple", "golden delicious apple"], "cut_or_form": ["dried apple"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_apple_brandy'})
SET i.canonical_name = 'apple brandy',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["apple brandies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_butter'})
SET i.canonical_name = 'apple butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["apple butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_cider'})
SET i.canonical_name = 'apple cider',
    i.category = 'beverage',
    i.base = 'cider',
    i.alt_names = ["apple ciders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_cider_vinegar'})
SET i.canonical_name = 'apple cider vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["apple cider vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_juice'})
SET i.canonical_name = 'apple juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["apple juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_juice_concentrate'})
SET i.canonical_name = 'apple juice concentrate',
    i.category = 'condiment',
    i.base = 'concentrate',
    i.alt_names = ["apple juice concentrates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_puree'})
SET i.canonical_name = 'apple puree',
    i.category = 'condiment',
    i.base = 'puree',
    i.alt_names = ["apple purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apple_schnapp'})
SET i.canonical_name = 'apple schnapp',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["apple schnapps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_applesauce'})
SET i.canonical_name = 'applesauce',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["applesauces"],
    i.variations = '{"other": ["applesauce"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_apricot'})
SET i.canonical_name = 'apricot',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["apricots"],
    i.variations = '{"other": ["apricot"], "cut_or_form": ["dried apricot"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_apricot_brandy'})
SET i.canonical_name = 'apricot brandy',
    i.category = 'fruit',
    i.base = 'apricot',
    i.alt_names = ["apricot brandies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apricot_jam'})
SET i.canonical_name = 'apricot jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["apricot jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apricot_nectar'})
SET i.canonical_name = 'apricot nectar',
    i.category = 'fruit',
    i.base = 'apricot',
    i.alt_names = ["apricot nectars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_apricot_preserve'})
SET i.canonical_name = 'apricot preserve',
    i.category = 'fruit',
    i.base = 'apricot',
    i.alt_names = ["apricot preserves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_arborio_rice'})
SET i.canonical_name = 'arborio rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["arborio rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_arepa_flour'})
SET i.canonical_name = 'arepa flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["arepa flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_aril'})
SET i.canonical_name = 'aril',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["arils"],
    i.variations = '{"other": ["aril"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_arrowroot_flour'})
SET i.canonical_name = 'arrowroot flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["arrowroot flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_arrowroot_powder'})
SET i.canonical_name = 'arrowroot powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["arrowroot powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_artichok'})
SET i.canonical_name = 'artichok',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["artichoks"],
    i.variations = '{"other": ["artichok", "baby artichok"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_artichoke'})
SET i.canonical_name = 'artichoke',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["artichokes"],
    i.variations = '{"other": ["artichoke"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_artichoke_bottom'})
SET i.canonical_name = 'artichoke bottom',
    i.category = 'vegetable',
    i.base = 'artichoke',
    i.alt_names = ["artichoke bottoms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_artichoke_heart'})
SET i.canonical_name = 'artichoke heart',
    i.category = 'vegetable',
    i.base = 'artichoke',
    i.alt_names = ["artichoke hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_artisan_bread'})
SET i.canonical_name = 'artisan bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["artisan breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_arugula'})
SET i.canonical_name = 'arugula',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["arugulas"],
    i.variations = '{"other": ["arugula", "baby arugula"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_asafetida_powder'})
SET i.canonical_name = 'asafetida powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["asafetida powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_asafoetida_powder'})
SET i.canonical_name = 'asafoetida powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["asafoetida powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_asparagus'})
SET i.canonical_name = 'asparagus',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["asparaguses"],
    i.variations = '{"other": ["asparagus"], "cut_or_form": ["fresh asparagus"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_asparagus_bean'})
SET i.canonical_name = 'asparagus bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["asparagus beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_asparagus_spear'})
SET i.canonical_name = 'asparagus spear',
    i.category = 'vegetable',
    i.base = 'asparagus',
    i.alt_names = ["asparagus spears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_asparagus_tip'})
SET i.canonical_name = 'asparagus tip',
    i.category = 'vegetable',
    i.base = 'asparagus',
    i.alt_names = ["asparagus tips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_atlantic_cod_fillet'})
SET i.canonical_name = 'atlantic cod fillet',
    i.category = 'seafood',
    i.base = 'cod',
    i.alt_names = ["atlantic cod fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_avocado'})
SET i.canonical_name = 'avocado',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["avocados"],
    i.variations = '{"other": ["avocado"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_avocado_leaf'})
SET i.canonical_name = 'avocado leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["avocado leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_avocado_oil'})
SET i.canonical_name = 'avocado oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["avocado oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_azteca_flour_tortilla'})
SET i.canonical_name = 'azteca flour tortilla',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["azteca flour tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_azuki_bean'})
SET i.canonical_name = 'azuki bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["azuki beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_a_ai_powder'})
SET i.canonical_name = 'açai powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["açai powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_baby'})
SET i.canonical_name = 'baby',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["babies"],
    i.variations = '{"other": ["baby", "baby octopu"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bacon'})
SET i.canonical_name = 'bacon',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["bacons"],
    i.variations = '{"product": ["bacon"], "cut_or_form": ["applewood smoked bacon", "smoked bacon", "smoked streaky bacon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bacon_salt'})
SET i.canonical_name = 'bacon salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["bacon salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bagel'})
SET i.canonical_name = 'bagel',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["bagels"],
    i.variations = '{"other": ["bagel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bagel_chip'})
SET i.canonical_name = 'bagel chip',
    i.category = 'grain',
    i.base = 'bagel',
    i.alt_names = ["bagel chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_baguette'})
SET i.canonical_name = 'baguette',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["baguettes"],
    i.variations = '{"other": ["baguette"], "cut_or_form": ["whole grain baguette", "whole wheat baguette"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_balm_leaf'})
SET i.canonical_name = 'balm leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["balm leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_balsamic_vinegar'})
SET i.canonical_name = 'balsamic vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["balsamic vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bamboo_shoot'})
SET i.canonical_name = 'bamboo shoot',
    i.category = 'vegetable',
    i.base = 'shoot',
    i.alt_names = ["bamboo shoots"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana'})
SET i.canonical_name = 'banana',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["bananas"],
    i.variations = '{"other": ["banana"], "cut_or_form": ["frozen banana"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_banana_blossom'})
SET i.canonical_name = 'banana blossom',
    i.category = 'herb',
    i.base = 'blossom',
    i.alt_names = ["banana blossoms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_bread'})
SET i.canonical_name = 'banana bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["banana breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_chip'})
SET i.canonical_name = 'banana chip',
    i.category = 'fruit',
    i.base = 'banana',
    i.alt_names = ["banana chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_flower'})
SET i.canonical_name = 'banana flower',
    i.category = 'fruit',
    i.base = 'banana',
    i.alt_names = ["banana flowers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_leaf'})
SET i.canonical_name = 'banana leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["banana leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_liqueur'})
SET i.canonical_name = 'banana liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["banana liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_pepper'})
SET i.canonical_name = 'banana pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["banana peppers"],
    i.variations = null;

// Progress: 100/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_banana_puree'})
SET i.canonical_name = 'banana puree',
    i.category = 'condiment',
    i.base = 'puree',
    i.alt_names = ["banana purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banana_squash'})
SET i.canonical_name = 'banana squash',
    i.category = 'vegetable',
    i.base = 'squash',
    i.alt_names = ["banana squashes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_banh_pho_rice_noodle'})
SET i.canonical_name = 'banh pho rice noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["banh pho rice noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_barbecue_sauce'})
SET i.canonical_name = 'barbecue sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["barbecue sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_barbecued_pork'})
SET i.canonical_name = 'barbecued pork',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["barbecued porks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_barberry'})
SET i.canonical_name = 'barberry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["barberries"],
    i.variations = '{"other": ["barberry"], "cut_or_form": ["dried barberry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_barley'})
SET i.canonical_name = 'barley',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["barleies"],
    i.variations = '{"other": ["barley"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_barley_flak'})
SET i.canonical_name = 'barley flak',
    i.category = 'grain',
    i.base = 'barley',
    i.alt_names = ["barley flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_barley_flour'})
SET i.canonical_name = 'barley flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["barley flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_barley_miso'})
SET i.canonical_name = 'barley miso',
    i.category = 'condiment',
    i.base = 'miso',
    i.alt_names = ["barley misos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bartlett_pear'})
SET i.canonical_name = 'bartlett pear',
    i.category = 'fruit',
    i.base = 'pear',
    i.alt_names = ["bartlett pears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_basil'})
SET i.canonical_name = 'basil',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["basils"],
    i.variations = '{"other": ["basil"], "cut_or_form": ["dried basil"], "grade_style": ["sweet basil"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_basil_leaf'})
SET i.canonical_name = 'basil leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["basil leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_basil_mayonnaise'})
SET i.canonical_name = 'basil mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["basil mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_basil_olive_oil'})
SET i.canonical_name = 'basil olive oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["basil olive oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_basil_pesto_sauce'})
SET i.canonical_name = 'basil pesto sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["basil pesto sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_basmati_rice'})
SET i.canonical_name = 'basmati rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["basmati rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bay_leaf'})
SET i.canonical_name = 'bay leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["bay leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bbq_sauce'})
SET i.canonical_name = 'bbq sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["bbq sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean'})
SET i.canonical_name = 'bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["beans"],
    i.variations = '{"other": ["baby lima bean", "bean", "bean curd stick", "kroger black bean", "refried bean", "refried black bean", "seasoned black bean", "string bean", "sweetened red bean", "vegetarian refried bean", "yardlong bean"], "cut_or_form": ["canned bean", "canned black bean", "dried bean", "dried black bean", "dried kidney bean", "dried navy bean", "dried pinto bean", "fresh bean", "fresh fava bean", "fresh green bean", "fresh lima bean", "frozen broad bean", "frozen edamame bean", "frozen green bean", "frozen lima bean"], "nutrition": ["light kidney bean", "light red kidney bean", "low sodium black bean", "low sodium garbanzo bean", "low sodium pinto bean", "reduced sodium black bean", "reduced sodium kidney bean", "reduced sodium refried bean"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bean_curd'})
SET i.canonical_name = 'bean curd',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["bean curds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_curd_skin'})
SET i.canonical_name = 'bean curd skin',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["bean curd skins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_dip'})
SET i.canonical_name = 'bean dip',
    i.category = 'condiment',
    i.base = 'dip',
    i.alt_names = ["bean dips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_paste'})
SET i.canonical_name = 'bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_sauce'})
SET i.canonical_name = 'bean sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["bean sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_soup'})
SET i.canonical_name = 'bean soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["bean soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_thread'})
SET i.canonical_name = 'bean thread',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["bean threads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bean_thread_vermicelli'})
SET i.canonical_name = 'bean thread vermicelli',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["bean thread vermicellis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef'})
SET i.canonical_name = 'beef',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["beefes", "beefs", "beeves"],
    i.variations = '{"other": ["beef", "beef round"], "cut_or_form": ["boneless beef chuck roast", "boneless beef short rib", "cubed beef", "dried beef", "ground beef", "lean ground beef"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_beef_bon'})
SET i.canonical_name = 'beef bon',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_bouillon'})
SET i.canonical_name = 'beef bouillon',
    i.category = 'condiment',
    i.base = 'bouillon',
    i.alt_names = ["beef bouillons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_bouillon_granule'})
SET i.canonical_name = 'beef bouillon granule',
    i.category = 'condiment',
    i.base = 'bouillon',
    i.alt_names = ["beef bouillon granules"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_bouillon_powder'})
SET i.canonical_name = 'beef bouillon powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["beef bouillon powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_brisket'})
SET i.canonical_name = 'beef brisket',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef briskets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_broth'})
SET i.canonical_name = 'beef broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["beef broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_carpaccio'})
SET i.canonical_name = 'beef carpaccio',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef carpaccios"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_cheek'})
SET i.canonical_name = 'beef cheek',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef cheeks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_consomme'})
SET i.canonical_name = 'beef consomme',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef consommes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_demi_glace'})
SET i.canonical_name = 'beef demi-glace',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef demi-glaces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_fillet'})
SET i.canonical_name = 'beef fillet',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_gravy'})
SET i.canonical_name = 'beef gravy',
    i.category = 'condiment',
    i.base = 'gravy',
    i.alt_names = ["beef gravies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_heart'})
SET i.canonical_name = 'beef heart',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_hot_dog'})
SET i.canonical_name = 'beef hot dog',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef hot dogs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_jerky'})
SET i.canonical_name = 'beef jerky',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef jerkies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_kidney'})
SET i.canonical_name = 'beef kidney',
    i.category = 'plant_protein',
    i.base = 'kidney',
    i.alt_names = ["beef kidneies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_liver'})
SET i.canonical_name = 'beef liver',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef livers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_marrow'})
SET i.canonical_name = 'beef marrow',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef marrows"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_rib'})
SET i.canonical_name = 'beef rib',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef ribs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_rib_roast'})
SET i.canonical_name = 'beef rib roast',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef rib roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_rib_short'})
SET i.canonical_name = 'beef rib short',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef rib shorts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_roast'})
SET i.canonical_name = 'beef roast',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_rump'})
SET i.canonical_name = 'beef rump',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef rumps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_rump_steak'})
SET i.canonical_name = 'beef rump steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["beef rump steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_sausage'})
SET i.canonical_name = 'beef sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["beef sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_shank'})
SET i.canonical_name = 'beef shank',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef shanks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_shin'})
SET i.canonical_name = 'beef shin',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef shins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_shoulder'})
SET i.canonical_name = 'beef shoulder',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef shoulders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_shoulder_roast'})
SET i.canonical_name = 'beef shoulder roast',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef shoulder roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_sirloin'})
SET i.canonical_name = 'beef sirloin',
    i.category = 'meat',
    i.base = 'sirloin',
    i.alt_names = ["beef sirloins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_soup_bon'})
SET i.canonical_name = 'beef soup bon',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["beef soup bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_steak'})
SET i.canonical_name = 'beef steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["beef steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_stew'})
SET i.canonical_name = 'beef stew',
    i.category = 'condiment',
    i.base = 'stew',
    i.alt_names = ["beef stews"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_stew_meat'})
SET i.canonical_name = 'beef stew meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["beef stew meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_stock'})
SET i.canonical_name = 'beef stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["beef stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_stock_cub'})
SET i.canonical_name = 'beef stock cub',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["beef stock cubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_strip'})
SET i.canonical_name = 'beef strip',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef strips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_tenderloin'})
SET i.canonical_name = 'beef tenderloin',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef tenderloins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_tenderloin_steak'})
SET i.canonical_name = 'beef tenderloin steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["beef tenderloin steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_tendon'})
SET i.canonical_name = 'beef tendon',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef tendons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beef_tongue'})
SET i.canonical_name = 'beef tongue',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["beef tongues"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beefsteak_tomato'})
SET i.canonical_name = 'beefsteak tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["beefsteak tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beer'})
SET i.canonical_name = 'beer',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["beers"],
    i.variations = '{"other": ["root beer"], "nutrition": ["light beer"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_beer_batter'})
SET i.canonical_name = 'beer batter',
    i.category = 'beverage',
    i.base = 'beer',
    i.alt_names = ["beer batters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beet'})
SET i.canonical_name = 'beet',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["beets"],
    i.variations = '{"other": ["baby beet", "beet", "golden beet"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_beet_green'})
SET i.canonical_name = 'beet green',
    i.category = 'vegetable',
    i.base = 'green',
    i.alt_names = ["beet greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beet_juice'})
SET i.canonical_name = 'beet juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["beet juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bell'})
SET i.canonical_name = 'bell',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["bells"],
    i.variations = '{"variety": ["bell"], "grade_style": ["sweet mini bell"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bell_pepper'})
SET i.canonical_name = 'bell pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["bell peppers", "bellpepper", "bellpeppers", "capsicum", "sweet pepper"],
    i.variations = '{"other": ["green bell pepper", "orange bell pepper", "purple bell pepper", "red bell pepper", "yellow bell pepper"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_beluga_caviar'})
SET i.canonical_name = 'beluga caviar',
    i.category = 'seafood',
    i.base = 'caviar',
    i.alt_names = ["beluga caviars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_beluga_lentil'})
SET i.canonical_name = 'beluga lentil',
    i.category = 'plant_protein',
    i.base = 'lentil',
    i.alt_names = ["beluga lentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bermuda_onion'})
SET i.canonical_name = 'bermuda onion',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["bermuda onions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_berry'})
SET i.canonical_name = 'berry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["berries"],
    i.variations = '{"other": ["berry"], "cut_or_form": ["dried allspice berry", "whole wheat berry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bibb_lettuce'})
SET i.canonical_name = 'bibb lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["bibb lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bing_cherry'})
SET i.canonical_name = 'bing cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["bing cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bird_pepper'})
SET i.canonical_name = 'bird pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["bird peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_biscotti'})
SET i.canonical_name = 'biscotti',
    i.category = 'baking',
    i.base = null,
    i.alt_names = ["biscottis"],
    i.variations = '{"other": ["biscotti"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_biscuit_dough'})
SET i.canonical_name = 'biscuit dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["biscuit doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bison'})
SET i.canonical_name = 'bison',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["bisons"],
    i.variations = '{"other": ["bison"], "cut_or_form": ["ground bison"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bitter_chocolate'})
SET i.canonical_name = 'bitter chocolate',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["bitter chocolates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bitter_orange_juice'})
SET i.canonical_name = 'bitter orange juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["bitter orange juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black'})
SET i.canonical_name = 'black',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["blacks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_bean'})
SET i.canonical_name = 'black bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black beans", "blackbean", "blackbeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_bean_garlic_sauce'})
SET i.canonical_name = 'black bean garlic sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["black bean garlic sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_bean_sauce'})
SET i.canonical_name = 'black bean sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["black bean sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_cardamom_pod'})
SET i.canonical_name = 'black cardamom pod',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["black cardamom pods", "blackcardamompod", "blackcardamompods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_cherry'})
SET i.canonical_name = 'black cherry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["black cherries", "blackcherries", "blackcherry"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_chicken'})
SET i.canonical_name = 'black chicken',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["black chickens", "blackchicken", "blackchickens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_chickpea'})
SET i.canonical_name = 'black chickpea',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black chickpeas", "blackchickpea", "blackchickpeas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_cod'})
SET i.canonical_name = 'black cod',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["black cods", "blackcod", "blackcods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_cod_fillet'})
SET i.canonical_name = 'black cod fillet',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["black cod fillets", "blackcodfillet", "blackcodfillets"],
    i.variations = null;

// Progress: 200/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_black_currant'})
SET i.canonical_name = 'black currant',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["black currants", "blackcurrant", "blackcurrants"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_forest_ham'})
SET i.canonical_name = 'black forest ham',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["black forest hams", "blackforestham", "blackforesthams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_fungu'})
SET i.canonical_name = 'black fungu',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black fungus", "blackfungu", "blackfungus"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_garlic'})
SET i.canonical_name = 'black garlic',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["black garlics", "blackgarlic", "blackgarlics"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_gram'})
SET i.canonical_name = 'black gram',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black grams", "blackgram", "blackgrams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_grap'})
SET i.canonical_name = 'black grap',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["black graps", "blackgrap", "blackgraps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_lentil'})
SET i.canonical_name = 'black lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black lentils", "blacklentil", "blacklentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_mos'})
SET i.canonical_name = 'black mos',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black mo", "black moses", "blackmo", "blackmos", "blackmoses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_mushroom'})
SET i.canonical_name = 'black mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["black mushrooms", "blackmushroom", "blackmushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_olive'})
SET i.canonical_name = 'black olive',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["black olives", "blackolive", "blackolives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_pepper'})
SET i.canonical_name = 'black pepper',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["black peppers", "blackpepper", "blackpeppers"],
    i.variations = '{"other": ["coars ground black pepper", "cracked black pepper", "ground black pepper"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_black_peppercorn'})
SET i.canonical_name = 'black peppercorn',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["black peppercorns", "blackpeppercorn", "blackpeppercorns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_quinoa'})
SET i.canonical_name = 'black quinoa',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["black quinoas", "blackquinoa", "blackquinoas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_radish'})
SET i.canonical_name = 'black radish',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["black radishes", "blackradish", "blackradishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_rice'})
SET i.canonical_name = 'black rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["black rices", "blackrice", "blackrices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_rice_vinegar'})
SET i.canonical_name = 'black rice vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["black rice vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_salt'})
SET i.canonical_name = 'black salt',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["black salts", "blacksalt", "blacksalts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_sticky_rice'})
SET i.canonical_name = 'black sticky rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["black sticky rices", "blackstickyrice", "blackstickyrices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_tea'})
SET i.canonical_name = 'black tea',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["black teas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_tea_leaf'})
SET i.canonical_name = 'black tea leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["black tea leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_treacle'})
SET i.canonical_name = 'black treacle',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black treacles", "blacktreacle", "blacktreacles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_truffle'})
SET i.canonical_name = 'black truffle',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black truffles", "blacktruffle", "blacktruffles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_truffle_oil'})
SET i.canonical_name = 'black truffle oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["black truffle oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_trumpet_mushroom'})
SET i.canonical_name = 'black trumpet mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["black trumpet mushrooms", "blacktrumpetmushroom", "blacktrumpetmushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_turtle_bean'})
SET i.canonical_name = 'black turtle bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black turtle beans", "blackturtlebean", "blackturtlebeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_vinegar'})
SET i.canonical_name = 'black vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["black vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_walnut'})
SET i.canonical_name = 'black walnut',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["black walnuts", "blackwalnut", "blackwalnuts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_black_eyed_pea'})
SET i.canonical_name = 'black-eyed pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["black-eyed peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blackbean'})
SET i.canonical_name = 'blackbean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["black bean", "black beans", "blackbeans"],
    i.variations = '{"other": ["blackbean"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_blackberry_brandy'})
SET i.canonical_name = 'blackberry brandy',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["blackberry brandies", "blackberrybrandies", "blackberrybrandy"],
    i.variations = '{"other": ["blackberry brandy"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_blackberry_jam'})
SET i.canonical_name = 'blackberry jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["blackberry jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blackcurrant_syrup'})
SET i.canonical_name = 'blackcurrant syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["blackcurrant syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blackstrap_molasses'})
SET i.canonical_name = 'blackstrap molasses',
    i.category = 'sweetener',
    i.base = 'molasses',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blanched_almond_flour'})
SET i.canonical_name = 'blanched almond flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["blanched almond flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blood_orange'})
SET i.canonical_name = 'blood orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["blood oranges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blood_orange_juice'})
SET i.canonical_name = 'blood orange juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["blood orange juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blossom'})
SET i.canonical_name = 'blossom',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["blossoms"],
    i.variations = '{"cut_or_form": ["dried hibiscus blossom", "dried lavender blossom"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_blue_cheese'})
SET i.canonical_name = 'blue cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["blue cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blue_corn_tortilla_chip'})
SET i.canonical_name = 'blue corn tortilla chip',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["blue corn tortilla chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_blueberry_jam'})
SET i.canonical_name = 'blueberry jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["blueberry jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_boar'})
SET i.canonical_name = 'boar',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["boars"],
    i.variations = '{"other": ["boar"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bock_beer'})
SET i.canonical_name = 'bock beer',
    i.category = 'beverage',
    i.base = 'beer',
    i.alt_names = ["bock beers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bok_choy'})
SET i.canonical_name = 'bok choy',
    i.category = 'vegetable',
    i.base = 'choy',
    i.alt_names = ["bok choies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bologna'})
SET i.canonical_name = 'bologna',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["bolognas"],
    i.variations = '{"other": ["bologna"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bolognese'})
SET i.canonical_name = 'bolognese',
    i.category = 'sauce',
    i.base = null,
    i.alt_names = ["bologneses"],
    i.variations = '{"other": ["bolognese"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bone_broth'})
SET i.canonical_name = 'bone broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["bone broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_boned_lamb_shoulder'})
SET i.canonical_name = 'boned lamb shoulder',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["boned lamb shoulders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bonito'})
SET i.canonical_name = 'bonito',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["bonitos"],
    i.variations = '{"other": ["bonito"], "cut_or_form": ["dried bonito"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bonito_flak'})
SET i.canonical_name = 'bonito flak',
    i.category = 'seafood',
    i.base = 'bonito',
    i.alt_names = ["bonito flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bordelaise_sauce'})
SET i.canonical_name = 'bordelaise sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["bordelaise sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_borlotti_bean'})
SET i.canonical_name = 'borlotti bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["borlotti beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bosc_pear'})
SET i.canonical_name = 'bosc pear',
    i.category = 'fruit',
    i.base = 'pear',
    i.alt_names = ["bosc pears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_boston_lettuce'})
SET i.canonical_name = 'boston lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["boston lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bouillon'})
SET i.canonical_name = 'bouillon',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["bouillons"],
    i.variations = '{"flavor_source": ["fish bouillon cube", "instant chicken bouillon", "instant chicken bouillon granule", "lamb bouillon cube", "pork bouillon cube", "vegetable bouillon cube"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bouillon_powder'})
SET i.canonical_name = 'bouillon powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["bouillon powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bouillon_shrimp'})
SET i.canonical_name = 'bouillon shrimp',
    i.category = 'condiment',
    i.base = 'bouillon',
    i.alt_names = ["bouillon shrimps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bourbon_liqueur'})
SET i.canonical_name = 'bourbon liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["bourbon liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_boy_choy'})
SET i.canonical_name = 'boy choy',
    i.category = 'vegetable',
    i.base = 'choy',
    i.alt_names = ["boy choies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_braeburn_apple'})
SET i.canonical_name = 'braeburn apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["braeburn apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_braising_beef'})
SET i.canonical_name = 'braising beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["braising beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bramley_apple'})
SET i.canonical_name = 'bramley apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["bramley apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bran_flak'})
SET i.canonical_name = 'bran flak',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["bran flaks", "branflak", "branflaks"],
    i.variations = '{"other": ["bran flak"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_branston_pickle'})
SET i.canonical_name = 'branston pickle',
    i.category = 'condiment',
    i.base = 'pickle',
    i.alt_names = ["branston pickles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bratwurst'})
SET i.canonical_name = 'bratwurst',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["bratwursts"],
    i.variations = '{"other": ["bratwurst"], "cut_or_form": ["smoked bratwurst"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bread'})
SET i.canonical_name = 'bread',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["breads"],
    i.variations = '{"other": ["bread", "country bread", "country white bread", "crumbled corn bread", "round sourdough bread"], "cut_or_form": ["cubed bread", "whole grain bread", "whole wheat bread", "whole wheat peasant bread", "whole wheat pita bread", "whole wheat sandwich bread", "whole wheat sourdough bread"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bread_ciabatta'})
SET i.canonical_name = 'bread ciabatta',
    i.category = 'grain',
    i.base = 'ciabatta',
    i.alt_names = ["bread ciabattas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bread_dough'})
SET i.canonical_name = 'bread dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["bread doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bread_flour'})
SET i.canonical_name = 'bread flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["bread flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bread_machine_yeast'})
SET i.canonical_name = 'bread machine yeast',
    i.category = 'baking',
    i.base = 'yeast',
    i.alt_names = ["bread machine yeasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bread_roll'})
SET i.canonical_name = 'bread roll',
    i.category = 'grain',
    i.base = 'roll',
    i.alt_names = ["bread rolls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bread_slice'})
SET i.canonical_name = 'bread slice',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["bread slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bread_yeast'})
SET i.canonical_name = 'bread yeast',
    i.category = 'baking',
    i.base = 'yeast',
    i.alt_names = ["bread yeasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_breadcrumb'})
SET i.canonical_name = 'breadcrumb',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["bread crumb", "bread crumbs", "breadcrumbs"],
    i.variations = '{"other": ["breadcrumb", "unseasoned breadcrumb"], "cut_or_form": ["whole wheat breadcrumb", "whole wheat seasoned breadcrumb"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_breadfruit'})
SET i.canonical_name = 'breadfruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["bread fruit", "bread fruits", "breadfruits"],
    i.variations = '{"other": ["breadfruit"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_breast'})
SET i.canonical_name = 'breast',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["breasts"],
    i.variations = '{"cut_or_form": ["boneless chicken breast", "boneless duck breast", "boneless moulard duck breast", "boneless skinless chicken breast", "boneless, skinless chicken breast", "breast", "canned chicken breast", "free range chicken breast", "ground chicken breast", "skinless chicken breast"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_brie_cheese'})
SET i.canonical_name = 'brie cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["brie cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brioche_bread'})
SET i.canonical_name = 'brioche bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["brioche breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broad_bean'})
SET i.canonical_name = 'broad bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["broad beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli'})
SET i.canonical_name = 'broccoli',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["broccolis"],
    i.variations = '{"other": ["baby broccoli", "broccoli"], "cut_or_form": ["frozen broccoli"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli_floret'})
SET i.canonical_name = 'broccoli floret',
    i.category = 'vegetable',
    i.base = 'broccoli',
    i.alt_names = ["broccoli florets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli_rabe'})
SET i.canonical_name = 'broccoli rabe',
    i.category = 'vegetable',
    i.base = 'broccoli',
    i.alt_names = ["broccoli rabes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli_romanesco'})
SET i.canonical_name = 'broccoli romanesco',
    i.category = 'vegetable',
    i.base = 'broccoli',
    i.alt_names = ["broccoli romanescos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli_slaw'})
SET i.canonical_name = 'broccoli slaw',
    i.category = 'vegetable',
    i.base = 'broccoli',
    i.alt_names = ["broccoli slaws"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli_sprout'})
SET i.canonical_name = 'broccoli sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["broccoli sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_broccoli_stem'})
SET i.canonical_name = 'broccoli stem',
    i.category = 'vegetable',
    i.base = 'broccoli',
    i.alt_names = ["broccoli stems"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bronzino'})
SET i.canonical_name = 'bronzino',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["bronzinos"],
    i.variations = '{"other": ["bronzino"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_broth'})
SET i.canonical_name = 'broth',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["broths"],
    i.variations = '{"flavor_source": ["canned beef broth", "canned chicken broth", "fatfree lowsodium chicken broth", "homemade chicken broth", "less sodium beef broth", "less sodium chicken broth", "low salt chicken broth", "low sodium beef broth", "low sodium chicken broth", "low sodium vegetable broth", "lower sodium beef broth", "lower sodium chicken broth", "no-chicken broth", "nonfat beef broth", "nonfat chicken broth", "organic chicken broth", "organic vegetable broth", "reduced sodium beef broth", "reduced sodium chicken broth", "reduced sodium vegetable broth", "sodium free chicken broth", "sodium reduced beef broth", "sodium reduced chicken broth"], "nutrition": ["low sodium broth"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_brown_ale'})
SET i.canonical_name = 'brown ale',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["brown ales", "brownale", "brownales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_basmati_rice'})
SET i.canonical_name = 'brown basmati rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["brown basmati rices", "brownbasmatirice", "brownbasmatirices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_beech_mushroom'})
SET i.canonical_name = 'brown beech mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["brown beech mushrooms", "brownbeechmushroom", "brownbeechmushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_butter'})
SET i.canonical_name = 'brown butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["brown butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_cardamom'})
SET i.canonical_name = 'brown cardamom',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["brown cardamoms", "browncardamom", "browncardamoms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_chicken_stock'})
SET i.canonical_name = 'brown chicken stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["brown chicken stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_gravy'})
SET i.canonical_name = 'brown gravy',
    i.category = 'condiment',
    i.base = 'gravy',
    i.alt_names = ["brown gravies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_hash_potato'})
SET i.canonical_name = 'brown hash potato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["brown hash potatos", "brownhashpotato", "brownhashpotatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_lentil'})
SET i.canonical_name = 'brown lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["brown lentils", "brownlentil", "brownlentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_mushroom'})
SET i.canonical_name = 'brown mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["brown mushrooms", "brownmushroom", "brownmushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_mustard'})
SET i.canonical_name = 'brown mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["brown mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice'})
SET i.canonical_name = 'brown rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["brown rices", "brownrice", "brownrices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice_flour'})
SET i.canonical_name = 'brown rice flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["brown rice flours"],
    i.variations = null;

// Progress: 300/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice_noodle'})
SET i.canonical_name = 'brown rice noodle',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["brown rice noodles", "brownricenoodle", "brownricenoodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice_penne'})
SET i.canonical_name = 'brown rice penne',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["brown rice pennes", "brownricepenne", "brownricepennes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice_spaghetti'})
SET i.canonical_name = 'brown rice spaghetti',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["brown rice spaghettis", "brownricespaghetti", "brownricespaghettis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice_syrup'})
SET i.canonical_name = 'brown rice syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["brown rice syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_rice_vinegar'})
SET i.canonical_name = 'brown rice vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["brown rice vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_sauce'})
SET i.canonical_name = 'brown sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["brown sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_shrimp'})
SET i.canonical_name = 'brown shrimp',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["brown shrimps", "brownshrimp", "brownshrimps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brown_sugar'})
SET i.canonical_name = 'brown sugar',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["brown sugars", "brownsugar", "brownsugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_brussels_sprout'})
SET i.canonical_name = 'brussels sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["brussels sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bucatini'})
SET i.canonical_name = 'bucatini',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["bucatinis"],
    i.variations = '{"other": ["bucatini"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_buckwheat'})
SET i.canonical_name = 'buckwheat',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["buckwheats"],
    i.variations = '{"other": ["buckwheat", "raw buckwheat groat"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_buckwheat_flour'})
SET i.canonical_name = 'buckwheat flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["buckwheat flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buckwheat_groat'})
SET i.canonical_name = 'buckwheat groat',
    i.category = 'grain',
    i.base = 'buckwheat',
    i.alt_names = ["buckwheat groats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buckwheat_honey'})
SET i.canonical_name = 'buckwheat honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["buckwheat honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buckwheat_noodle'})
SET i.canonical_name = 'buckwheat noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["buckwheat noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buckwheat_soba_noodle'})
SET i.canonical_name = 'buckwheat soba noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["buckwheat soba noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buffalo'})
SET i.canonical_name = 'buffalo',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["buffalos"],
    i.variations = '{"other": ["buffalo"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_buffalo_meat'})
SET i.canonical_name = 'buffalo meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["buffalo meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buffalo_mozarella'})
SET i.canonical_name = 'buffalo mozarella',
    i.category = 'meat',
    i.base = 'buffalo',
    i.alt_names = ["buffalo mozarellas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buffalo_mozzarella'})
SET i.canonical_name = 'buffalo mozzarella',
    i.category = 'dairy',
    i.base = 'mozzarella',
    i.alt_names = ["buffalo mozzarellas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buffalo_sauce'})
SET i.canonical_name = 'buffalo sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["buffalo sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bulb_fennel'})
SET i.canonical_name = 'bulb fennel',
    i.category = 'vegetable',
    i.base = 'fennel',
    i.alt_names = ["bulb fennels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_bulgur'})
SET i.canonical_name = 'bulgur',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["bulgurs"],
    i.variations = '{"other": ["bulgur"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_bulgur_wheat'})
SET i.canonical_name = 'bulgur wheat',
    i.category = 'grain',
    i.base = 'wheat',
    i.alt_names = ["bulgur wheats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_burgundy_wine'})
SET i.canonical_name = 'burgundy wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["burgundy wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_burro_banana'})
SET i.canonical_name = 'burro banana',
    i.category = 'fruit',
    i.base = 'banana',
    i.alt_names = ["burro bananas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter'})
SET i.canonical_name = 'butter',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["butters"],
    i.variations = '{"other": ["challenge butter", "clarified butter", "grass-fed butter", "pumpkin butter", "smooth natural peanut butter", "softened butter", "stick butter", "vegan butter", "whipped butter"], "grade_style": ["kerrygold pure irish butter", "organic butter", "sweet cream butter"], "nutrition": ["light butter"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_butter_bean'})
SET i.canonical_name = 'butter bean',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["butter beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_cake'})
SET i.canonical_name = 'butter cake',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["butter cakes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_cooky'})
SET i.canonical_name = 'butter cooky',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["butter cookies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_cracker'})
SET i.canonical_name = 'butter cracker',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["butter crackers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_lettuce'})
SET i.canonical_name = 'butter lettuce',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["butter lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_oil'})
SET i.canonical_name = 'butter oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["butter oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_pecan_ice_cream'})
SET i.canonical_name = 'butter pecan ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["butter pecan ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_salt'})
SET i.canonical_name = 'butter salt',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["butter salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_butter_margarine_blend'})
SET i.canonical_name = 'butter-margarine blend',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["butter-margarine blends", "butter-margarineblend", "butter-margarineblends"],
    i.variations = '{"other": ["butter-margarine blend"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_butterhead_lettuce'})
SET i.canonical_name = 'butterhead lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["butterhead lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_buttermilk'})
SET i.canonical_name = 'buttermilk',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["buttermilks"],
    i.variations = '{"other": ["buttermilk", "powdered buttermilk"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_butterscotch_chip'})
SET i.canonical_name = 'butterscotch chip',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["butterscotch chips", "butterscotchchip", "butterscotchchips"],
    i.variations = '{"other": ["butterscotch chip"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_butterscotch_sauce'})
SET i.canonical_name = 'butterscotch sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["butterscotch sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_button_mushroom'})
SET i.canonical_name = 'button mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["button mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cabbage'})
SET i.canonical_name = 'cabbage',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["cabbages"],
    i.variations = '{"other": ["cabbage"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cabbage_head'})
SET i.canonical_name = 'cabbage head',
    i.category = 'vegetable',
    i.base = 'cabbage',
    i.alt_names = ["cabbage heads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cabbage_leaf'})
SET i.canonical_name = 'cabbage leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["cabbage leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cabbage_lettuce'})
SET i.canonical_name = 'cabbage lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["cabbage lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cacao_powder'})
SET i.canonical_name = 'cacao powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["cacao powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cactus_leaf'})
SET i.canonical_name = 'cactus leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["cactus leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cake'})
SET i.canonical_name = 'cake',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["cakes"],
    i.variations = '{"other": ["angel food cake", "cake", "cake pound prepar", "sponge cake", "store-bought pound cake"], "cut_or_form": ["frozen pound cake"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cake_batter'})
SET i.canonical_name = 'cake batter',
    i.category = 'grain',
    i.base = 'cake',
    i.alt_names = ["cake batters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cake_flour'})
SET i.canonical_name = 'cake flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["cake flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cake_yeast'})
SET i.canonical_name = 'cake yeast',
    i.category = 'baking',
    i.base = 'yeast',
    i.alt_names = ["cake yeasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_calamansi_juice'})
SET i.canonical_name = 'calamansi juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["calamansi juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_calamata_olive'})
SET i.canonical_name = 'calamata olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["calamata olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_california_avocado'})
SET i.canonical_name = 'california avocado',
    i.category = 'fruit',
    i.base = 'avocado',
    i.alt_names = ["california avocados"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_california_bay_leaf'})
SET i.canonical_name = 'california bay leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["california bay leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_camellia_red_kidney_bean'})
SET i.canonical_name = 'camellia red kidney bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["camellia red kidney beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candied_cherry'})
SET i.canonical_name = 'candied cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["candied cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candied_fruit'})
SET i.canonical_name = 'candied fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["candied fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candied_ginger'})
SET i.canonical_name = 'candied ginger',
    i.category = 'seasoning',
    i.base = 'ginger',
    i.alt_names = ["candied gingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candied_lemon_peel'})
SET i.canonical_name = 'candied lemon peel',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["candied lemon peels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candied_orange_peel'})
SET i.canonical_name = 'candied orange peel',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["candied orange peels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candied_pineapple'})
SET i.canonical_name = 'candied pineapple',
    i.category = 'fruit',
    i.base = 'pineapple',
    i.alt_names = ["candied pineapples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_candy'})
SET i.canonical_name = 'candy',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["candies"],
    i.variations = '{"other": ["candy"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cane_sugar'})
SET i.canonical_name = 'cane sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["cane sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cane_syrup'})
SET i.canonical_name = 'cane syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["cane syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cane_vinegar'})
SET i.canonical_name = 'cane vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["cane vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cannellini_bean'})
SET i.canonical_name = 'cannellini bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["cannellini beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_canning_salt'})
SET i.canonical_name = 'canning salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["canning salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_canola'})
SET i.canonical_name = 'canola',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["canolas"],
    i.variations = '{"other": ["canola"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_canola_mayonnaise'})
SET i.canonical_name = 'canola mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["canola mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_canola_oil'})
SET i.canonical_name = 'canola oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["canola oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_caper'})
SET i.canonical_name = 'caper',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["capers"],
    i.variations = '{"other": ["caper"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cara_cara_orange'})
SET i.canonical_name = 'cara cara orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["cara cara oranges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_caramel_ice_cream'})
SET i.canonical_name = 'caramel ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["caramel ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_caramel_sauce'})
SET i.canonical_name = 'caramel sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["caramel sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_caramel_syrup'})
SET i.canonical_name = 'caramel syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["caramel syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cardamom'})
SET i.canonical_name = 'cardamom',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["cardamoms"],
    i.variations = '{"other": ["cardamom"], "cut_or_form": ["ground cardamom"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cardamom_pod'})
SET i.canonical_name = 'cardamom pod',
    i.category = 'seasoning',
    i.base = 'cardamom',
    i.alt_names = ["cardamom pods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_carnaroli_rice'})
SET i.canonical_name = 'carnaroli rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["carnaroli rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_carrot'})
SET i.canonical_name = 'carrot',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["carrots"],
    i.variations = '{"other": ["baby carrot", "carrot", "carrot stick"], "cut_or_form": ["frozen carrot"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_carrot_green'})
SET i.canonical_name = 'carrot green',
    i.category = 'vegetable',
    i.base = 'green',
    i.alt_names = ["carrot greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_carrot_juice'})
SET i.canonical_name = 'carrot juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["carrot juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cashew'})
SET i.canonical_name = 'cashew',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["cashews"],
    i.variations = '{"other": ["cashew", "raw cashew"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cashew_butter'})
SET i.canonical_name = 'cashew butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["cashew butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cashew_milk'})
SET i.canonical_name = 'cashew milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["cashew milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cassia_cinnamon'})
SET i.canonical_name = 'cassia cinnamon',
    i.category = 'seasoning',
    i.base = 'cinnamon',
    i.alt_names = ["cassia cinnamons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cassis_liqueur'})
SET i.canonical_name = 'cassis liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["cassis liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_caster_sugar'})
SET i.canonical_name = 'caster sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["caster sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cauliflower'})
SET i.canonical_name = 'cauliflower',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["cauliflowers"],
    i.variations = '{"other": ["cauliflower"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cauliflower_floret'})
SET i.canonical_name = 'cauliflower floret',
    i.category = 'vegetable',
    i.base = 'cauliflower',
    i.alt_names = ["cauliflower florets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cauliflower_floweret'})
SET i.canonical_name = 'cauliflower floweret',
    i.category = 'vegetable',
    i.base = 'cauliflower',
    i.alt_names = ["cauliflower flowerets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cavatappi'})
SET i.canonical_name = 'cavatappi',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["cavatappis"],
    i.variations = '{"other": ["cavatappi"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_caviar'})
SET i.canonical_name = 'caviar',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["caviars"],
    i.variations = '{"other": ["caviar"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cayenne_pepper'})
SET i.canonical_name = 'cayenne pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["cayenne peppers", "cayennepepper", "cayennepeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ceci_bean'})
SET i.canonical_name = 'ceci bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["ceci beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celery'})
SET i.canonical_name = 'celery',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["celeries"],
    i.variations = '{"other": ["celery", "celery root", "celery stick"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_celery_cabbage'})
SET i.canonical_name = 'celery cabbage',
    i.category = 'vegetable',
    i.base = 'cabbage',
    i.alt_names = ["celery cabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celery_flak'})
SET i.canonical_name = 'celery flak',
    i.category = 'vegetable',
    i.base = 'celery',
    i.alt_names = ["celery flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celery_heart'})
SET i.canonical_name = 'celery heart',
    i.category = 'vegetable',
    i.base = 'celery',
    i.alt_names = ["celery hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celery_leaf'})
SET i.canonical_name = 'celery leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["celery leafs"],
    i.variations = null;

// Progress: 400/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_celery_rib'})
SET i.canonical_name = 'celery rib',
    i.category = 'vegetable',
    i.base = 'celery',
    i.alt_names = ["celery ribs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celery_salt'})
SET i.canonical_name = 'celery salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["celery salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celery_top'})
SET i.canonical_name = 'celery top',
    i.category = 'vegetable',
    i.base = 'celery',
    i.alt_names = ["celery tops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_celtic_salt'})
SET i.canonical_name = 'celtic salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["celtic salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cereal'})
SET i.canonical_name = 'cereal',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["cereals"],
    i.variations = '{"other": ["cereal", "crispy rice cereal"], "cut_or_form": ["whole wheat cereal"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cereal_flak'})
SET i.canonical_name = 'cereal flak',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["cereal flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ceylon_cinnamon'})
SET i.canonical_name = 'ceylon cinnamon',
    i.category = 'seasoning',
    i.base = 'cinnamon',
    i.alt_names = ["ceylon cinnamons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chambord_liqueur'})
SET i.canonical_name = 'chambord liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["chambord liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_champagne_vinegar'})
SET i.canonical_name = 'champagne vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["champagne vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chapati_flour'})
SET i.canonical_name = 'chapati flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["chapati flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chapatti_flour'})
SET i.canonical_name = 'chapatti flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["chapatti flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_char_siu_sauce'})
SET i.canonical_name = 'char siu sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["char siu sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chard'})
SET i.canonical_name = 'chard',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["chards"],
    i.variations = '{"other": ["chard"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chartreuse_liqueur'})
SET i.canonical_name = 'chartreuse liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["chartreuse liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheddar_cheese'})
SET i.canonical_name = 'cheddar cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["cheddar cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheddar_cheese_soup'})
SET i.canonical_name = 'cheddar cheese soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["cheddar cheese soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese'})
SET i.canonical_name = 'cheese',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["cheeses"],
    i.variations = '{"other": ["aged cheddar cheese", "aged manchego cheese", "cheese", "cheese stick", "crumbled blue cheese", "crumbled cheese", "crumbled goat cheese", "crumbled ricotta salata cheese", "lowfat pepper jack cheese", "mozzarella string cheese", "parmigiano reggiano cheese", "parmigiano-reggiano cheese", "pecorino cheese", "pecorino romano cheese", "romano cheese", "sharp cheddar cheese", "sharp white cheddar cheese", "shaved parmesan cheese", "string cheese", "vegan cheese", "vegan parmesan cheese"], "cut_or_form": ["fresh cheese", "fresh parmesan cheese", "smoked cheddar cheese", "soft fresh goat cheese"], "product": ["taco seasoned cheese"], "nutrition": ["low sodium mozzarella cheese", "low sodium parmesan cheese", "nonfat cottage cheese", "nonfat mozzarella cheese", "nonfat ricotta cheese", "part-skim mozzarella cheese", "part-skim ricotta cheese"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_crouton'})
SET i.canonical_name = 'cheese crouton',
    i.category = 'grain',
    i.base = 'crouton',
    i.alt_names = ["cheese croutons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_cub'})
SET i.canonical_name = 'cheese cub',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["cheese cubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_curd'})
SET i.canonical_name = 'cheese curd',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["cheese curds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_dip'})
SET i.canonical_name = 'cheese dip',
    i.category = 'condiment',
    i.base = 'dip',
    i.alt_names = ["cheese dips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_ravioli'})
SET i.canonical_name = 'cheese ravioli',
    i.category = 'grain',
    i.base = 'ravioli',
    i.alt_names = ["cheese raviolis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_sauce'})
SET i.canonical_name = 'cheese sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["cheese sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_slice'})
SET i.canonical_name = 'cheese slice',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["cheese slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_soup'})
SET i.canonical_name = 'cheese soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["cheese soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cheese_tortellini'})
SET i.canonical_name = 'cheese tortellini',
    i.category = 'grain',
    i.base = 'tortellini',
    i.alt_names = ["cheese tortellinis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry'})
SET i.canonical_name = 'cherry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["cherries"],
    i.variations = '{"other": ["cherry", "pitted cherry"], "grade_style": ["sweet cherry"], "cut_or_form": ["dried cherry", "dried tart cherry", "frozen cherry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_brandy'})
SET i.canonical_name = 'cherry brandy',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["cherry brandies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_coke'})
SET i.canonical_name = 'cherry coke',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["cherry cokes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_gelatin'})
SET i.canonical_name = 'cherry gelatin',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["cherry gelatins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_juice'})
SET i.canonical_name = 'cherry juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["cherry juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_pepper'})
SET i.canonical_name = 'cherry pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["cherry peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_preserve'})
SET i.canonical_name = 'cherry preserve',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["cherry preserves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_syrup'})
SET i.canonical_name = 'cherry syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["cherry syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_tomato'})
SET i.canonical_name = 'cherry tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["cherry tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_vanilla_ice_cream'})
SET i.canonical_name = 'cherry vanilla ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["cherry vanilla ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherry_vinegar'})
SET i.canonical_name = 'cherry vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["cherry vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cherrystone_clam'})
SET i.canonical_name = 'cherrystone clam',
    i.category = 'seafood',
    i.base = 'clam',
    i.alt_names = ["cherrystone clams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chestnut'})
SET i.canonical_name = 'chestnut',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["chestnuts"],
    i.variations = '{"other": ["chestnut"], "cut_or_form": ["dried chestnut"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chestnut_flour'})
SET i.canonical_name = 'chestnut flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["chestnut flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chestnut_honey'})
SET i.canonical_name = 'chestnut honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["chestnut honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chestnut_mushroom'})
SET i.canonical_name = 'chestnut mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["chestnut mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken'})
SET i.canonical_name = 'chicken',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["chickens"],
    i.variations = '{"other": ["broiler chicken", "broiler-fryer chicken", "chicken", "free-range chicken", "rotisserie chicken", "spring chicken"], "cut_or_form": ["boneless chicken", "boneless chicken skinless thigh", "boneless skinless chicken", "breaded chicken fillet", "canned chicken", "frozen popcorn chicken", "ground chicken", "tyson crispy chicken strip", "whole chicken"], "grade_style": ["organic chicken"], "nutrition": ["low sodium chicken"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_bon'})
SET i.canonical_name = 'chicken bon',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_bouillon'})
SET i.canonical_name = 'chicken bouillon',
    i.category = 'condiment',
    i.base = 'bouillon',
    i.alt_names = ["chicken bouillons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_bouillon_granule'})
SET i.canonical_name = 'chicken bouillon granule',
    i.category = 'condiment',
    i.base = 'bouillon',
    i.alt_names = ["chicken bouillon granules"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_breast'})
SET i.canonical_name = 'chicken breast',
    i.category = 'meat',
    i.base = 'breast',
    i.alt_names = ["chicken breasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_breast_fillet'})
SET i.canonical_name = 'chicken breast fillet',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken breast fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_breast_strip'})
SET i.canonical_name = 'chicken breast strip',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken breast strips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_breast_tender'})
SET i.canonical_name = 'chicken breast tender',
    i.category = 'meat',
    i.base = 'tender',
    i.alt_names = ["chicken breast tenders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_breast_tenderloin'})
SET i.canonical_name = 'chicken breast tenderloin',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken breast tenderloins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_broth'})
SET i.canonical_name = 'chicken broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["chicken broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_carcas'})
SET i.canonical_name = 'chicken carcas',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_chorizo_sausage'})
SET i.canonical_name = 'chicken chorizo sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["chicken chorizo sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_consomme'})
SET i.canonical_name = 'chicken consomme',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken consommes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_cutlet'})
SET i.canonical_name = 'chicken cutlet',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken cutlets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_demi_glace'})
SET i.canonical_name = 'chicken demi-glace',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken demi-glaces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_drumstick'})
SET i.canonical_name = 'chicken drumstick',
    i.category = 'meat',
    i.base = 'drumstick',
    i.alt_names = ["chicken drumsticks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_egg'})
SET i.canonical_name = 'chicken egg',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["chicken eggs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_feet'})
SET i.canonical_name = 'chicken feet',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken feets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_fillet'})
SET i.canonical_name = 'chicken fillet',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_finger'})
SET i.canonical_name = 'chicken finger',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken fingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_gizzard'})
SET i.canonical_name = 'chicken gizzard',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken gizzards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_gravy'})
SET i.canonical_name = 'chicken gravy',
    i.category = 'condiment',
    i.base = 'gravy',
    i.alt_names = ["chicken gravies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_heart'})
SET i.canonical_name = 'chicken heart',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_leg'})
SET i.canonical_name = 'chicken leg',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_liver'})
SET i.canonical_name = 'chicken liver',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken livers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_meat'})
SET i.canonical_name = 'chicken meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["chicken meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_noodle_soup'})
SET i.canonical_name = 'chicken noodle soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["chicken noodle soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_nugget'})
SET i.canonical_name = 'chicken nugget',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken nuggets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_part'})
SET i.canonical_name = 'chicken part',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken parts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_piece'})
SET i.canonical_name = 'chicken piece',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken pieces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_sausage'})
SET i.canonical_name = 'chicken sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["chicken sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_schmaltz'})
SET i.canonical_name = 'chicken schmaltz',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken schmaltzs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_stock'})
SET i.canonical_name = 'chicken stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["chicken stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_stock_cub'})
SET i.canonical_name = 'chicken stock cub',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["chicken stock cubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_strip'})
SET i.canonical_name = 'chicken strip',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken strips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_tenderloin'})
SET i.canonical_name = 'chicken tenderloin',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken tenderloins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_thigh'})
SET i.canonical_name = 'chicken thigh',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken thighs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_thigh_fillet'})
SET i.canonical_name = 'chicken thigh fillet',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken thigh fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_wing_drummett'})
SET i.canonical_name = 'chicken wing drummett',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken wing drummetts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_wingett'})
SET i.canonical_name = 'chicken wingett',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["chicken wingetts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chicken_apple_sausage'})
SET i.canonical_name = 'chicken-apple sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["chicken-apple sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chickpea'})
SET i.canonical_name = 'chickpea',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["chickpeas"],
    i.variations = '{"other": ["chickpea"], "cut_or_form": ["dried chickpea"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chickpea_flour'})
SET i.canonical_name = 'chickpea flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["chickpea flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chihuahua_cheese'})
SET i.canonical_name = 'chihuahua cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["chihuahua cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chile'})
SET i.canonical_name = 'chile',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["chiles"],
    i.variations = '{"other": ["chile"], "cut_or_form": ["dried guajillo chile"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chilegarlic_sauce'})
SET i.canonical_name = 'chilegarlic sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chilegarlic sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili'})
SET i.canonical_name = 'chili',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["chile", "chilis", "chilli"],
    i.variations = '{"other": ["chili"], "cut_or_form": ["fresh red chili"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chili_bean'})
SET i.canonical_name = 'chili bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["chili beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_bean_paste'})
SET i.canonical_name = 'chili bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["chili bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_bean_sauce'})
SET i.canonical_name = 'chili bean sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chili bean sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_flak'})
SET i.canonical_name = 'chili flak',
    i.category = 'seasoning',
    i.base = 'chili',
    i.alt_names = ["chili flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_habanero_pepper'})
SET i.canonical_name = 'chili habanero pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["chili habanero peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_leaf'})
SET i.canonical_name = 'chili leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["chili leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_oil'})
SET i.canonical_name = 'chili oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["chili oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_paste'})
SET i.canonical_name = 'chili paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["chili pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_pepper'})
SET i.canonical_name = 'chili pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["chili peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_pepper_flak'})
SET i.canonical_name = 'chili pepper flak',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["chili pepper flaks", "chilipepperflak", "chilipepperflaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chili_powder'})
SET i.canonical_name = 'chili powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["chili powders"],
    i.variations = null;

// Progress: 500/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_chili_sauce'})
SET i.canonical_name = 'chili sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chili sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chilli_bean_sauce'})
SET i.canonical_name = 'chilli bean sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chilli bean sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chilli_paste'})
SET i.canonical_name = 'chilli paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["chilli pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chinkiang_vinegar'})
SET i.canonical_name = 'chinkiang vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["chinkiang vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chipotle'})
SET i.canonical_name = 'chipotle',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["chipotles"],
    i.variations = '{"other": ["chipotle"], "cut_or_form": ["canned chipotle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chipotle_paste'})
SET i.canonical_name = 'chipotle paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["chipotle pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chipotle_pepper'})
SET i.canonical_name = 'chipotle pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["chipotle peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chipotle_salsa'})
SET i.canonical_name = 'chipotle salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["chipotle salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chipotle_sauce'})
SET i.canonical_name = 'chipotle sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chipotle sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chipped_beef'})
SET i.canonical_name = 'chipped beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["chipped beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chive'})
SET i.canonical_name = 'chive',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["chives"],
    i.variations = '{"other": ["chive"], "cut_or_form": ["dried chive"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chive_blossom'})
SET i.canonical_name = 'chive blossom',
    i.category = 'herb',
    i.base = 'blossom',
    i.alt_names = ["chive blossoms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chive_flower'})
SET i.canonical_name = 'chive flower',
    i.category = 'herb',
    i.base = 'chive',
    i.alt_names = ["chive flowers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chobani_yogurt'})
SET i.canonical_name = 'chobani yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["chobani yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate'})
SET i.canonical_name = 'chocolate',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["chocolates"],
    i.variations = '{"other": ["chocolate", "chocolate stick", "mini chocolate chip", "shaved chocolate"], "grade_style": ["bittersweet chocolate", "bittersweet chocolate chip", "semi-sweet chocolate morsel", "semisweet vegan chocolate chip", "sweet chocolate", "unsweetened chocolate"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_bar'})
SET i.canonical_name = 'chocolate bar',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate bars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_candy'})
SET i.canonical_name = 'chocolate candy',
    i.category = 'sweetener',
    i.base = 'candy',
    i.alt_names = ["chocolate candies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_candy_bar'})
SET i.canonical_name = 'chocolate candy bar',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate candy bars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_chip'})
SET i.canonical_name = 'chocolate chip',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_chunk'})
SET i.canonical_name = 'chocolate chunk',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate chunks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_cookie'})
SET i.canonical_name = 'chocolate cookie',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate cookies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_cookie_crumb'})
SET i.canonical_name = 'chocolate cookie crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["chocolate cookie crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_curl'})
SET i.canonical_name = 'chocolate curl',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate curls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_drink'})
SET i.canonical_name = 'chocolate drink',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate drinks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_fudge_ice_cream'})
SET i.canonical_name = 'chocolate fudge ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["chocolate fudge ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_glaze'})
SET i.canonical_name = 'chocolate glaze',
    i.category = 'condiment',
    i.base = 'glaze',
    i.alt_names = ["chocolate glazes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_ice_cream'})
SET i.canonical_name = 'chocolate ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["chocolate ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_leaf'})
SET i.canonical_name = 'chocolate leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["chocolate leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_liqueur'})
SET i.canonical_name = 'chocolate liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["chocolate liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_milk'})
SET i.canonical_name = 'chocolate milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["chocolate milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_morsel'})
SET i.canonical_name = 'chocolate morsel',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate morsels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_mousse'})
SET i.canonical_name = 'chocolate mousse',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate mousses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_sandwich_cooky'})
SET i.canonical_name = 'chocolate sandwich cooky',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate sandwich cookies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_sauce'})
SET i.canonical_name = 'chocolate sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chocolate sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_sprinkle'})
SET i.canonical_name = 'chocolate sprinkle',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate sprinkles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_syrup'})
SET i.canonical_name = 'chocolate syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["chocolate syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_truffle'})
SET i.canonical_name = 'chocolate truffle',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate truffles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chocolate_wafer_cooky'})
SET i.canonical_name = 'chocolate wafer cooky',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["chocolate wafer cookies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chorizo'})
SET i.canonical_name = 'chorizo',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["chorizos"],
    i.variations = '{"product": ["chorizo", "sweet chorizo"], "cut_or_form": ["smoked chorizo"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_choy'})
SET i.canonical_name = 'choy',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["choies"],
    i.variations = '{"other": ["baby bok choy", "choy"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_choy_sum'})
SET i.canonical_name = 'choy sum',
    i.category = 'vegetable',
    i.base = 'choy',
    i.alt_names = ["choy sums"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chrysanthemum_leaf'})
SET i.canonical_name = 'chrysanthemum leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["chrysanthemum leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_mild_salsa'})
SET i.canonical_name = 'chunky mild salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["chunky mild salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_pasta_sauce'})
SET i.canonical_name = 'chunky pasta sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chunky pasta sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_peanut_butter'})
SET i.canonical_name = 'chunky peanut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["chunky peanut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_salsa'})
SET i.canonical_name = 'chunky salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["chunky salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_tomato'})
SET i.canonical_name = 'chunky tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["chunky tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_tomato_salsa'})
SET i.canonical_name = 'chunky tomato salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["chunky tomato salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chunky_tomato_sauce'})
SET i.canonical_name = 'chunky tomato sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["chunky tomato sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_chutney'})
SET i.canonical_name = 'chutney',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["chutneies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ciabatta'})
SET i.canonical_name = 'ciabatta',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["ciabattas"],
    i.variations = '{"other": ["ciabatta"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ciabatta_roll'})
SET i.canonical_name = 'ciabatta roll',
    i.category = 'grain',
    i.base = 'roll',
    i.alt_names = ["ciabatta rolls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cider'})
SET i.canonical_name = 'cider',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["ciders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cider_vinegar'})
SET i.canonical_name = 'cider vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["cider vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cilantro_leaf'})
SET i.canonical_name = 'cilantro leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["cilantro leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cilantro_pesto'})
SET i.canonical_name = 'cilantro pesto',
    i.category = 'condiment',
    i.base = 'pesto',
    i.alt_names = ["cilantro pestos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon'})
SET i.canonical_name = 'cinnamon',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["cinnamons"],
    i.variations = '{"other": ["cinnamon", "cinnamon stick", "saigon cinnamon", "true cinnamon"], "cut_or_form": ["ground cinnamon"], "grade_style": ["simply organic cinnamon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon_candy_can'})
SET i.canonical_name = 'cinnamon candy can',
    i.category = 'seasoning',
    i.base = 'cinnamon',
    i.alt_names = ["cinnamon candy cans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon_hot_candy'})
SET i.canonical_name = 'cinnamon hot candy',
    i.category = 'sweetener',
    i.base = 'candy',
    i.alt_names = ["cinnamon hot candies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon_ice_cream'})
SET i.canonical_name = 'cinnamon ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["cinnamon ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon_roll'})
SET i.canonical_name = 'cinnamon roll',
    i.category = 'grain',
    i.base = 'roll',
    i.alt_names = ["cinnamon rolls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon_sugar'})
SET i.canonical_name = 'cinnamon sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["cinnamon sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cinnamon_toast_crunch_cereal'})
SET i.canonical_name = 'cinnamon toast crunch cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["cinnamon toast crunch cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_citric_acid_powder'})
SET i.canonical_name = 'citric acid powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["citric acid powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_citrus_fruit'})
SET i.canonical_name = 'citrus fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["citrus fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_citrus_juice'})
SET i.canonical_name = 'citrus juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["citrus juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_clam'})
SET i.canonical_name = 'clam',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["clams"],
    i.variations = '{"other": ["clam", "hard shelled clam"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_clam_juice'})
SET i.canonical_name = 'clam juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["clam juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_clam_sauce'})
SET i.canonical_name = 'clam sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["clam sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_clamato_juice'})
SET i.canonical_name = 'clamato juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["clamato juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_classico_pasta_sauce'})
SET i.canonical_name = 'classico pasta sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["classico pasta sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_clear_honey'})
SET i.canonical_name = 'clear honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["clear honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_clementine_juice'})
SET i.canonical_name = 'clementine juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["clementine juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_clotted_cream'})
SET i.canonical_name = 'clotted cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["clotted creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cloud_ear'})
SET i.canonical_name = 'cloud ear',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["cloud ears", "cloudear", "cloudears"],
    i.variations = '{"other": ["cloud ear"], "cut_or_form": ["dried cloud ear"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_clove'})
SET i.canonical_name = 'clove',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["cloves"],
    i.variations = '{"other": ["clove"], "cut_or_form": ["whole clove"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_clover_honey'})
SET i.canonical_name = 'clover honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["clover honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coarse_kosher_salt'})
SET i.canonical_name = 'coarse kosher salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["coarse kosher salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coarse_salt'})
SET i.canonical_name = 'coarse salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["coarse salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coarse_sea_salt'})
SET i.canonical_name = 'coarse sea salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["coarse sea salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coarse_semolina'})
SET i.canonical_name = 'coarse semolina',
    i.category = 'grain',
    i.base = 'semolina',
    i.alt_names = ["coarse semolinas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coarse_sugar'})
SET i.canonical_name = 'coarse sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["coarse sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coarse_grain_salt'})
SET i.canonical_name = 'coarse-grain salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["coarse-grain salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cocktail_cherry'})
SET i.canonical_name = 'cocktail cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["cocktail cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cocktail_pumpernickel_bread'})
SET i.canonical_name = 'cocktail pumpernickel bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["cocktail pumpernickel breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cocktail_sauce'})
SET i.canonical_name = 'cocktail sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["cocktail sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cocoa'})
SET i.canonical_name = 'cocoa',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["cocoas"],
    i.variations = '{"other": ["cocoa"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_coconut'})
SET i.canonical_name = 'coconut',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["coconuts"],
    i.variations = '{"other": ["coconut", "creamed coconut", "dry coconut", "flaked coconut", "sweetened coconut", "sweetened coconut flak", "toasted coconut"], "cut_or_form": ["unsweetened dried coconut"], "grade_style": ["toasted unsweetened coconut"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_amino'})
SET i.canonical_name = 'coconut amino',
    i.category = 'fruit',
    i.base = 'coconut',
    i.alt_names = ["coconut aminos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_butter'})
SET i.canonical_name = 'coconut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["coconut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_chip'})
SET i.canonical_name = 'coconut chip',
    i.category = 'fruit',
    i.base = 'coconut',
    i.alt_names = ["coconut chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_cream'})
SET i.canonical_name = 'coconut cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["coconut creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_flak'})
SET i.canonical_name = 'coconut flak',
    i.category = 'fruit',
    i.base = 'coconut',
    i.alt_names = ["coconut flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_flour'})
SET i.canonical_name = 'coconut flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["coconut flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_juice'})
SET i.canonical_name = 'coconut juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["coconut juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_meat'})
SET i.canonical_name = 'coconut meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["coconut meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_milk'})
SET i.canonical_name = 'coconut milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["coconut milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_milk_powder'})
SET i.canonical_name = 'coconut milk powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["coconut milk powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_milk_yogurt'})
SET i.canonical_name = 'coconut milk yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["coconut milk yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_oil'})
SET i.canonical_name = 'coconut oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["coconut oils"],
    i.variations = null;

// Progress: 600/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_coconut_rum'})
SET i.canonical_name = 'coconut rum',
    i.category = 'fruit',
    i.base = 'coconut',
    i.alt_names = ["coconut rums"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_sugar'})
SET i.canonical_name = 'coconut sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["coconut sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_syrup'})
SET i.canonical_name = 'coconut syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["coconut syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_vinegar'})
SET i.canonical_name = 'coconut vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["coconut vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coconut_water'})
SET i.canonical_name = 'coconut water',
    i.category = 'beverage',
    i.base = 'water',
    i.alt_names = ["coconut waters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cod'})
SET i.canonical_name = 'cod',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["cods"],
    i.variations = '{"other": ["cod"], "cut_or_form": ["fresh cod", "skin-on cod fillet"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cod_cheek'})
SET i.canonical_name = 'cod cheek',
    i.category = 'seafood',
    i.base = 'cod',
    i.alt_names = ["cod cheeks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cod_fillet'})
SET i.canonical_name = 'cod fillet',
    i.category = 'seafood',
    i.base = 'cod',
    i.alt_names = ["cod fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cod_fish'})
SET i.canonical_name = 'cod fish',
    i.category = 'seafood',
    i.base = 'fish',
    i.alt_names = ["cod fishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cod_roe'})
SET i.canonical_name = 'cod roe',
    i.category = 'seafood',
    i.base = 'cod',
    i.alt_names = ["cod roes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coffee'})
SET i.canonical_name = 'coffee',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["coffees"],
    i.variations = '{"other": ["chocolate covered coffee bean"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_coffee_bean'})
SET i.canonical_name = 'coffee bean',
    i.category = 'beverage',
    i.base = 'coffee',
    i.alt_names = ["coffee beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coffee_ice_cream'})
SET i.canonical_name = 'coffee ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["coffee ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coffee_liqueur'})
SET i.canonical_name = 'coffee liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["coffee liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cointreau_liqueur'})
SET i.canonical_name = 'cointreau liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["cointreau liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_colby_cheese'})
SET i.canonical_name = 'colby cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["colby cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_colby_jack_cheese'})
SET i.canonical_name = 'colby jack cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["colby jack cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cold_milk'})
SET i.canonical_name = 'cold milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["cold milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coleslaw_seasoning_blend'})
SET i.canonical_name = 'coleslaw seasoning blend',
    i.category = 'seasoning',
    i.base = 'seasoning',
    i.alt_names = ["coleslaw seasoning blends"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_collard_green'})
SET i.canonical_name = 'collard green',
    i.category = 'vegetable',
    i.base = 'green',
    i.alt_names = ["collard greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_collard_green_leaf'})
SET i.canonical_name = 'collard green leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["collard green leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_collard_leaf'})
SET i.canonical_name = 'collard leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["collard leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_color_food_green'})
SET i.canonical_name = 'color food green',
    i.category = 'vegetable',
    i.base = 'green',
    i.alt_names = ["color food greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_comice_pear'})
SET i.canonical_name = 'comice pear',
    i.category = 'fruit',
    i.base = 'pear',
    i.alt_names = ["comice pears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_concentrate'})
SET i.canonical_name = 'concentrate',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["concentrates"],
    i.variations = '{"cut_or_form": ["frozen cranberry juice concentrate", "frozen orange juice concentrate"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_confectioners_sugar'})
SET i.canonical_name = 'confectioners sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["confectioners sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_confit_duck_leg'})
SET i.canonical_name = 'confit duck leg',
    i.category = 'meat',
    i.base = 'duck',
    i.alt_names = ["confit duck legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_converted_rice'})
SET i.canonical_name = 'converted rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["converted rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cook_egg_hard'})
SET i.canonical_name = 'cook egg hard',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["cook egg hards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cooki_vanilla_wafer'})
SET i.canonical_name = 'cooki vanilla wafer',
    i.category = 'sweetener',
    i.base = 'vanilla',
    i.alt_names = ["cooki vanilla wafers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cookie_crumb'})
SET i.canonical_name = 'cookie crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["cookie crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_coriander'})
SET i.canonical_name = 'coriander',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["cilantro", "corianders"],
    i.variations = '{"other": ["coriander"], "cut_or_form": ["fresh coriander", "ground coriander"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_coriander_powder'})
SET i.canonical_name = 'coriander powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["coriander powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corkscrew_pasta'})
SET i.canonical_name = 'corkscrew pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["corkscrew pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn'})
SET i.canonical_name = 'corn',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["corns"],
    i.variations = '{"other": ["baby corn", "corn"], "cut_or_form": ["canned corn", "corn kernel whole", "fresh corn", "frozen corn", "frozen sweet corn", "frozen whole kernel corn"], "grade_style": ["sweet corn", "sweet yellow corn"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_corn_bread'})
SET i.canonical_name = 'corn bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["corn breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_bread_crumb'})
SET i.canonical_name = 'corn bread crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["corn bread crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_chip'})
SET i.canonical_name = 'corn chip',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["corn chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_flak'})
SET i.canonical_name = 'corn flak',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["corn flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_flakes_cereal'})
SET i.canonical_name = 'corn flakes cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["corn flakes cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_flour'})
SET i.canonical_name = 'corn flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["corn flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_husk'})
SET i.canonical_name = 'corn husk',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["corn husks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_kernel'})
SET i.canonical_name = 'corn kernel',
    i.category = 'grain',
    i.base = 'kernel',
    i.alt_names = ["corn kernels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_muffin'})
SET i.canonical_name = 'corn muffin',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["corn muffins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_niblet'})
SET i.canonical_name = 'corn niblet',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["corn niblets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_oil'})
SET i.canonical_name = 'corn oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["corn oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_salsa'})
SET i.canonical_name = 'corn salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["corn salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_starch'})
SET i.canonical_name = 'corn starch',
    i.category = 'grain',
    i.base = 'starch',
    i.alt_names = ["corn starches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_syrup'})
SET i.canonical_name = 'corn syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["corn syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_tortilla'})
SET i.canonical_name = 'corn tortilla',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["corn tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_tortilla_chip'})
SET i.canonical_name = 'corn tortilla chip',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["corn tortilla chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corn_on_the_cob'})
SET i.canonical_name = 'corn-on-the-cob',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["corn-on-the-cobs"],
    i.variations = '{"other": ["corn-on-the-cob"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cornbread_crumb'})
SET i.canonical_name = 'cornbread crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["cornbread crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_corned_beef'})
SET i.canonical_name = 'corned beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["corned beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cornflake_cereal'})
SET i.canonical_name = 'cornflake cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["cornflake cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cornflake_crumb'})
SET i.canonical_name = 'cornflake crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["cornflake crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cornhusk'})
SET i.canonical_name = 'cornhusk',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["cornhusks"],
    i.variations = '{"other": ["cornhusk"], "cut_or_form": ["dried cornhusk"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cornichon'})
SET i.canonical_name = 'cornichon',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["cornichons"],
    i.variations = '{"other": ["cornichon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cornmeal'})
SET i.canonical_name = 'cornmeal',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["cornmeals"],
    i.variations = '{"other": ["cornmeal", "self-rising cornmeal"], "cut_or_form": ["stone-ground cornmeal"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cornstarch'})
SET i.canonical_name = 'cornstarch',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["cornstarches"],
    i.variations = '{"other": ["cornstarch"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cortland_apple'})
SET i.canonical_name = 'cortland apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["cortland apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cottage_cheese'})
SET i.canonical_name = 'cottage cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["cottage cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_couscous'})
SET i.canonical_name = 'couscous',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["couscouses"],
    i.variations = '{"other": ["couscous", "instant couscous"], "cut_or_form": ["whole wheat couscous"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_crab'})
SET i.canonical_name = 'crab',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["crabs"],
    i.variations = '{"other": ["crab", "crab stick"], "cut_or_form": ["whole crab"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_crab_boil'})
SET i.canonical_name = 'crab boil',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["crab boils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crab_claw'})
SET i.canonical_name = 'crab claw',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["crab claws"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crab_leg'})
SET i.canonical_name = 'crab leg',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["crab legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crab_meat'})
SET i.canonical_name = 'crab meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["crab meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crabmeat'})
SET i.canonical_name = 'crabmeat',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["crabmeats"],
    i.variations = '{"other": ["crabmeat"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cracker'})
SET i.canonical_name = 'cracker',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["crackers"],
    i.variations = '{"other": ["chocolate graham cracker", "cinnamon graham cracker", "cracker", "graham cracker", "honey graham cracker"], "cut_or_form": ["whole wheat cracker"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cracker_crumb'})
SET i.canonical_name = 'cracker crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["cracker crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cracker_meal'})
SET i.canonical_name = 'cracker meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["cracker meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_craisin'})
SET i.canonical_name = 'craisin',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["craisins"],
    i.variations = '{"other": ["craisin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cranberry'})
SET i.canonical_name = 'cranberry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["cranberries"],
    i.variations = '{"other": ["cranberry"], "cut_or_form": ["dried cranberry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cranberry_bean'})
SET i.canonical_name = 'cranberry bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["cranberry beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cranberry_juice'})
SET i.canonical_name = 'cranberry juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["cranberry juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cranberry_juice_cocktail'})
SET i.canonical_name = 'cranberry juice cocktail',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["cranberry juice cocktails"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cranberry_sauce'})
SET i.canonical_name = 'cranberry sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["cranberry sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crawfish'})
SET i.canonical_name = 'crawfish',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["crawfishes"],
    i.variations = '{"other": ["crawfish"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cream'})
SET i.canonical_name = 'cream',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["creams"],
    i.variations = '{"other": ["cream cheese lowfat", "cream cheese, soften", "cream ic peach", "cream lowfat", "knudsen sour cream", "vegan sour cream", "whipped cream", "whipped cream cheese"], "nutrition": ["knudsen light sour cream", "light cream", "light cream cheese", "light sour cream", "light whipping cream", "non dairy sour cream", "nonfat block cream cheese", "nonfat cream cheese"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cream_cheese'})
SET i.canonical_name = 'cream cheese',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["cream cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cream_powder'})
SET i.canonical_name = 'cream powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["cream powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cream_sauce'})
SET i.canonical_name = 'cream sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["cream sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cream_sherry'})
SET i.canonical_name = 'cream sherry',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["cream sherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cream_sweeten_whip'})
SET i.canonical_name = 'cream sweeten whip',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["cream sweeten whips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cream_yogurt'})
SET i.canonical_name = 'cream yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["cream yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_creamy_peanut_butter'})
SET i.canonical_name = 'creamy peanut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["creamy peanut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crema'})
SET i.canonical_name = 'crema',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["cremas"],
    i.variations = '{"other": ["crema"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_creme'})
SET i.canonical_name = 'creme',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["cremes"],
    i.variations = '{"other": ["creme"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_creme_fraiche'})
SET i.canonical_name = 'creme fraiche',
    i.category = 'dairy',
    i.base = 'creme',
    i.alt_names = ["creme fraiches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cremini_mushroom'})
SET i.canonical_name = 'cremini mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["cremini mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_creole_mustard'})
SET i.canonical_name = 'creole mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["creole mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crimini_mushroom'})
SET i.canonical_name = 'crimini mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["crimini mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_croissant_dough'})
SET i.canonical_name = 'croissant dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["croissant doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crouton'})
SET i.canonical_name = 'crouton',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["croutons"],
    i.variations = '{"other": ["crouton"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_crumb'})
SET i.canonical_name = 'crumb',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["crumbs"],
    i.variations = '{"cut_or_form": ["bread crumb fresh"], "other": ["chocolate graham cracker crumb", "dry bread crumb", "graham cracker crumb", "seasoned bread crumb", "seasoned panko bread crumb"], "grade_style": ["sweet biscuit crumb"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_crust'})
SET i.canonical_name = 'crust',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["crusts"],
    i.variations = '{"other": ["crust", "graham cracker crust", "graham cracker pie crust", "prepared pie crust", "unbaked pie crust"], "cut_or_form": ["frozen pie crust", "whole wheat pizza crust"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_crusty_bread'})
SET i.canonical_name = 'crusty bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["crusty breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crystal_farms_butter'})
SET i.canonical_name = 'crystal farms butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["crystal farms butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_crystal_hot_sauce'})
SET i.canonical_name = 'crystal hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["crystal hot sauces"],
    i.variations = null;

// Progress: 700/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_crystallized_ginger'})
SET i.canonical_name = 'crystallized ginger',
    i.category = 'seasoning',
    i.base = 'ginger',
    i.alt_names = ["crystallized gingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cuban_pepper'})
SET i.canonical_name = 'cuban pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["cuban peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cucumber'})
SET i.canonical_name = 'cucumber',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["cucumbers"],
    i.variations = '{"other": ["cucumber"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cumin'})
SET i.canonical_name = 'cumin',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["cumins"],
    i.variations = '{"other": ["cumin"], "cut_or_form": ["goya ground cumin", "ground cumin", "roasted ground cumin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_cured_beef'})
SET i.canonical_name = 'cured beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["cured beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_cured_pork'})
SET i.canonical_name = 'cured pork',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["cured porks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curing_salt'})
SET i.canonical_name = 'curing salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["curing salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curly_kale'})
SET i.canonical_name = 'curly kale',
    i.category = 'vegetable',
    i.base = 'kale',
    i.alt_names = ["curly kales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curly_leaf_spinach'})
SET i.canonical_name = 'curly leaf spinach',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["curly leaf spinaches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curly_leaf_parsley'})
SET i.canonical_name = 'curly-leaf parsley',
    i.category = 'herb',
    i.base = 'parsley',
    i.alt_names = ["curly-leaf parsleies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_currant'})
SET i.canonical_name = 'currant',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["currants"],
    i.variations = '{"other": ["currant"], "cut_or_form": ["dried currant"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_curry'})
SET i.canonical_name = 'curry',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["curries"],
    i.variations = '{"cut_or_form": ["fresh curry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_curry_leaf'})
SET i.canonical_name = 'curry leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["curry leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curry_paste'})
SET i.canonical_name = 'curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curry_powder'})
SET i.canonical_name = 'curry powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["curry powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_curry_sauce'})
SET i.canonical_name = 'curry sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["curry sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_custard_powder'})
SET i.canonical_name = 'custard powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["custard powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_daikon'})
SET i.canonical_name = 'daikon',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["daikons"],
    i.variations = '{"other": ["daikon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_daikon_sprout'})
SET i.canonical_name = 'daikon sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["daikon sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_daisy_sour_cream'})
SET i.canonical_name = 'daisy sour cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["daisy sour creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dandelion_green'})
SET i.canonical_name = 'dandelion green',
    i.category = 'vegetable',
    i.base = 'green',
    i.alt_names = ["dandelion greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_darjeeling_tea_leaf'})
SET i.canonical_name = 'darjeeling tea leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["darjeeling tea leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dashi_powder'})
SET i.canonical_name = 'dashi powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["dashi powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dat'})
SET i.canonical_name = 'dat',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["dats"],
    i.variations = '{"other": ["dat"], "cut_or_form": ["dried dat"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_date_molasses'})
SET i.canonical_name = 'date molasses',
    i.category = 'sweetener',
    i.base = 'molasses',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_date_sugar'})
SET i.canonical_name = 'date sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["date sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_day_old_bread'})
SET i.canonical_name = 'day old bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["day old breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_deep_dish_pie_crust'})
SET i.canonical_name = 'deep dish pie crust',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["deep dish pie crusts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_delallo_penne_ziti'})
SET i.canonical_name = 'delallo penne ziti',
    i.category = 'grain',
    i.base = 'ziti',
    i.alt_names = ["delallo penne zitis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_demerara_sugar'})
SET i.canonical_name = 'demerara sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["demerara sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dende_oil'})
SET i.canonical_name = 'dende oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["dende oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dessert_wine'})
SET i.canonical_name = 'dessert wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["dessert wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_deveined_shrimp'})
SET i.canonical_name = 'deveined shrimp',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["deveined shrimps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dhaniya_powder'})
SET i.canonical_name = 'dhaniya powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["dhaniya powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dijon_mustard'})
SET i.canonical_name = 'dijon mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["dijon mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dill'})
SET i.canonical_name = 'dill',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["dills"],
    i.variations = '{"other": ["dill"], "cut_or_form": ["dried dill"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_dill_pickle'})
SET i.canonical_name = 'dill pickle',
    i.category = 'condiment',
    i.base = 'pickle',
    i.alt_names = ["dill pickles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dill_pickle_spear'})
SET i.canonical_name = 'dill pickle spear',
    i.category = 'herb',
    i.base = 'dill',
    i.alt_names = ["dill pickle spears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dinosaur_kale'})
SET i.canonical_name = 'dinosaur kale',
    i.category = 'vegetable',
    i.base = 'kale',
    i.alt_names = ["dinosaur kales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dip'})
SET i.canonical_name = 'dip',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["dips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dipping_chocolate'})
SET i.canonical_name = 'dipping chocolate',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["dipping chocolates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ditalini_pasta'})
SET i.canonical_name = 'ditalini pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["ditalini pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_doritos_tortilla_chip'})
SET i.canonical_name = 'doritos tortilla chip',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["doritos tortilla chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dough'})
SET i.canonical_name = 'dough',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["doughs"],
    i.variations = '{"other": ["dough", "mini phyllo dough shell", "refrigerated bread dough", "refrigerated seamless crescent dough"], "product": ["refrigerated pizza dough"], "cut_or_form": ["frozen bread dough", "frozen pizza dough", "whole wheat bread dough", "whole wheat dough", "whole wheat pizza dough"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_dragon_fruit'})
SET i.canonical_name = 'dragon fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["dragon fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dri_fruit_tropic'})
SET i.canonical_name = 'dri fruit tropic',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["dri fruit tropics"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_drumstick'})
SET i.canonical_name = 'drumstick',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["drumsticks"],
    i.variations = '{"cut_or_form": ["drumstick", "foster farms chicken drumstick"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_dubliner_cheese'})
SET i.canonical_name = 'dubliner cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["dubliner cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck'})
SET i.canonical_name = 'duck',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["ducks"],
    i.variations = '{"other": ["duck"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_duck_bon'})
SET i.canonical_name = 'duck bon',
    i.category = 'meat',
    i.base = 'duck',
    i.alt_names = ["duck bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck_breast'})
SET i.canonical_name = 'duck breast',
    i.category = 'meat',
    i.base = 'breast',
    i.alt_names = ["duck breasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck_drumstick'})
SET i.canonical_name = 'duck drumstick',
    i.category = 'meat',
    i.base = 'drumstick',
    i.alt_names = ["duck drumsticks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck_egg'})
SET i.canonical_name = 'duck egg',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["duck eggs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck_liver'})
SET i.canonical_name = 'duck liver',
    i.category = 'meat',
    i.base = 'duck',
    i.alt_names = ["duck livers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck_sauce'})
SET i.canonical_name = 'duck sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["duck sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_duck_stock'})
SET i.canonical_name = 'duck stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["duck stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_dumpling_dough'})
SET i.canonical_name = 'dumpling dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["dumpling doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_durum_wheat_flour'})
SET i.canonical_name = 'durum wheat flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["durum wheat flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_earl_grey_tea_leaf'})
SET i.canonical_name = 'earl grey tea leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["earl grey tea leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_eating_apple'})
SET i.canonical_name = 'eating apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["eating apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_edamame_bean'})
SET i.canonical_name = 'edamame bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["edamame beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_edible_gold_leaf'})
SET i.canonical_name = 'edible gold leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["edible gold leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_eel'})
SET i.canonical_name = 'eel',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["eels"],
    i.variations = '{"other": ["eel"], "cut_or_form": ["smoked eel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_egg'})
SET i.canonical_name = 'egg',
    i.category = 'baking',
    i.base = null,
    i.alt_names = ["eggs"],
    i.variations = '{"other": ["egg", "flax egg", "free range egg", "free-range egg", "hard-boiled egg", "powdered egg whit", "soft-boiled egg"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_egg_beater'})
SET i.canonical_name = 'egg beater',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["egg beaters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_bread'})
SET i.canonical_name = 'egg bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["egg breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_noodle'})
SET i.canonical_name = 'egg noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["egg noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_pasta'})
SET i.canonical_name = 'egg pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["egg pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_roll_skin'})
SET i.canonical_name = 'egg roll skin',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["egg roll skins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_roll_wrap'})
SET i.canonical_name = 'egg roll wrap',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["egg roll wraps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_roll_wrapper'})
SET i.canonical_name = 'egg roll wrapper',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["egg roll wrappers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_whit'})
SET i.canonical_name = 'egg whit',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["egg whits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_egg_yolk'})
SET i.canonical_name = 'egg yolk',
    i.category = 'baking',
    i.base = 'yolk',
    i.alt_names = ["egg yolks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_eggplant'})
SET i.canonical_name = 'eggplant',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["aubergine", "eggplants"],
    i.variations = '{"other": ["eggplant"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_elbow_macaroni'})
SET i.canonical_name = 'elbow macaroni',
    i.category = 'grain',
    i.base = 'macaroni',
    i.alt_names = ["elbow macaronis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_elbow_pasta'})
SET i.canonical_name = 'elbow pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["elbow pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_elderflower_syrup'})
SET i.canonical_name = 'elderflower syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["elderflower syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_empanada_dough'})
SET i.canonical_name = 'empanada dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["empanada doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_enchilada_sauce'})
SET i.canonical_name = 'enchilada sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["enchilada sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_enriched_white_rice'})
SET i.canonical_name = 'enriched white rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["enriched white rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_espresso'})
SET i.canonical_name = 'espresso',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["espressos"],
    i.variations = '{"other": ["chocolatecovered espresso bean"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_espresso_bean'})
SET i.canonical_name = 'espresso bean',
    i.category = 'beverage',
    i.base = 'espresso',
    i.alt_names = ["espresso beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_espresso_powder'})
SET i.canonical_name = 'espresso powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["espresso powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_essence'})
SET i.canonical_name = 'essence',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["essences"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_evaporated_cane_juice'})
SET i.canonical_name = 'evaporated cane juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["evaporated cane juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_evaporated_milk'})
SET i.canonical_name = 'evaporated milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["evaporated milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fajita_size_flour_tortilla'})
SET i.canonical_name = 'fajita size flour tortilla',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["fajita size flour tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_farfalle'})
SET i.canonical_name = 'farfalle',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["farfalles"],
    i.variations = '{"other": ["farfalle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_farmer_cheese'})
SET i.canonical_name = 'farmer cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["farmer cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_farro'})
SET i.canonical_name = 'farro',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["farros"],
    i.variations = '{"other": ["farro"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fast_rising_yeast'})
SET i.canonical_name = 'fast rising yeast',
    i.category = 'baking',
    i.base = 'yeast',
    i.alt_names = ["fast rising yeasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fava_bean'})
SET i.canonical_name = 'fava bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["fava beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fennel'})
SET i.canonical_name = 'fennel',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["fennels"],
    i.variations = '{"other": ["fennel"], "cut_or_form": ["ground fennel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fennel_bulb'})
SET i.canonical_name = 'fennel bulb',
    i.category = 'vegetable',
    i.base = 'fennel',
    i.alt_names = ["fennel bulbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fennel_frond'})
SET i.canonical_name = 'fennel frond',
    i.category = 'vegetable',
    i.base = 'fennel',
    i.alt_names = ["fennel fronds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fenugreek_leaf'})
SET i.canonical_name = 'fenugreek leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["fenugreek leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fermented_bean_curd'})
SET i.canonical_name = 'fermented bean curd',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["fermented bean curds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fermented_bean_paste'})
SET i.canonical_name = 'fermented bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["fermented bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fermented_black_bean'})
SET i.canonical_name = 'fermented black bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["fermented black beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_feta'})
SET i.canonical_name = 'feta',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["fetas"],
    i.variations = '{"other": ["feta"]}';

// Progress: 800/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_feta_cheese'})
SET i.canonical_name = 'feta cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["feta cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_feta_cheese_crumble'})
SET i.canonical_name = 'feta cheese crumble',
    i.category = 'dairy',
    i.base = 'feta',
    i.alt_names = ["feta cheese crumbles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fettuccine'})
SET i.canonical_name = 'fettuccine',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["fettuccines"],
    i.variations = '{"other": ["dry fettuccine", "fettuccine", "refrigerated fettuccine"], "cut_or_form": ["dried fettuccine", "whole wheat fettuccine"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fettuccine_pasta'})
SET i.canonical_name = 'fettuccine pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["fettuccine pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fideos_pasta'})
SET i.canonical_name = 'fideos pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["fideos pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_field_lettuce'})
SET i.canonical_name = 'field lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["field lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_field_pea'})
SET i.canonical_name = 'field pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["field peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fig'})
SET i.canonical_name = 'fig',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["figs"],
    i.variations = '{"other": ["fig"], "cut_or_form": ["dried fig"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fillet_red_snapper'})
SET i.canonical_name = 'fillet red snapper',
    i.category = 'seafood',
    i.base = 'snapper',
    i.alt_names = ["fillet red snappers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_filo_dough'})
SET i.canonical_name = 'filo dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["filo doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fine_egg_noodle'})
SET i.canonical_name = 'fine egg noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["fine egg noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fine_grain_salt'})
SET i.canonical_name = 'fine grain salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["fine grain salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fine_granulated_sugar'})
SET i.canonical_name = 'fine granulated sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["fine granulated sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fine_salt'})
SET i.canonical_name = 'fine salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["fine salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fine_sea_salt'})
SET i.canonical_name = 'fine sea salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["fine sea salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish'})
SET i.canonical_name = 'fish',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["fishes"],
    i.variations = '{"other": ["fish"], "cut_or_form": ["dried fish flak", "smoked & dried fish"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fish_ball'})
SET i.canonical_name = 'fish ball',
    i.category = 'seafood',
    i.base = 'fish',
    i.alt_names = ["fish balls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_bon'})
SET i.canonical_name = 'fish bon',
    i.category = 'seafood',
    i.base = 'fish',
    i.alt_names = ["fish bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_broth'})
SET i.canonical_name = 'fish broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["fish broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_fillet'})
SET i.canonical_name = 'fish fillet',
    i.category = 'seafood',
    i.base = 'fish',
    i.alt_names = ["fish fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_finger'})
SET i.canonical_name = 'fish finger',
    i.category = 'seafood',
    i.base = 'fish',
    i.alt_names = ["fish fingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_paste'})
SET i.canonical_name = 'fish paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["fish pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_sauce'})
SET i.canonical_name = 'fish sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["fish sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_steak'})
SET i.canonical_name = 'fish steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["fish steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fish_stock'})
SET i.canonical_name = 'fish stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["fish stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_flat_anchovy'})
SET i.canonical_name = 'flat anchovy',
    i.category = 'seafood',
    i.base = 'anchovy',
    i.alt_names = ["flat anchovies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_flat_leaf_parsley'})
SET i.canonical_name = 'flat leaf parsley',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["flat leaf parsleies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_flat_leaf_spinach'})
SET i.canonical_name = 'flat leaf spinach',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["flat leaf spinaches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_flatbread'})
SET i.canonical_name = 'flatbread',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["flatbreads"],
    i.variations = '{"other": ["flatbread"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_flour'})
SET i.canonical_name = 'flour',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["flours"],
    i.variations = '{"other": ["cassava root flour", "graham flour", "seasoned flour", "self rising flour", "self-rising cake flour", "steamed bun flour", "strong white bread flour", "unbleached flour"], "grade_style": ["all purpose unbleached flour", "all-purpose flour", "sweet rice flour"], "cut_or_form": ["whole grain spelt flour", "whole wheat bread flour", "whole wheat flour", "whole wheat pastry flour", "whole wheat white flour"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_flour_tortilla'})
SET i.canonical_name = 'flour tortilla',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["flour tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_flowering_garlic_chive'})
SET i.canonical_name = 'flowering garlic chive',
    i.category = 'herb',
    i.base = 'chive',
    i.alt_names = ["flowering garlic chives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fontina_cheese'})
SET i.canonical_name = 'fontina cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["fontina cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_food_paste_color'})
SET i.canonical_name = 'food paste color',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["food paste colors"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_forest_fruit'})
SET i.canonical_name = 'forest fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["forest fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fowl'})
SET i.canonical_name = 'fowl',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["fowls"],
    i.variations = '{"other": ["fowl"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_framboise_liqueur'})
SET i.canonical_name = 'framboise liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["framboise liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_frankfurter'})
SET i.canonical_name = 'frankfurter',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["frankfurters"],
    i.variations = '{"other": ["frankfurter"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_franks_hot_sauce'})
SET i.canonical_name = 'franks hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["franks hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_franks_wings_sauce'})
SET i.canonical_name = 'franks wings sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["franks wings sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fruit'})
SET i.canonical_name = 'fruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["fruits"],
    i.variations = '{"other": ["fruit"], "cut_or_form": ["dried fruit", "frozen fruit"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fruit_cocktail'})
SET i.canonical_name = 'fruit cocktail',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["fruit cocktails"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fruit_juice'})
SET i.canonical_name = 'fruit juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["fruit juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fruit_puree'})
SET i.canonical_name = 'fruit puree',
    i.category = 'condiment',
    i.base = 'puree',
    i.alt_names = ["fruit purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_frying_oil'})
SET i.canonical_name = 'frying oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["frying oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_fuji_apple'})
SET i.canonical_name = 'fuji apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["fuji apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_furikake'})
SET i.canonical_name = 'furikake',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["furikakes"],
    i.variations = '{"other": ["furikake"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_fusilli'})
SET i.canonical_name = 'fusilli',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["fusillis"],
    i.variations = '{"other": ["fusilli"], "cut_or_form": ["whole wheat fusilli"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_gaeta_olive'})
SET i.canonical_name = 'gaeta olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["gaeta olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gala_apple'})
SET i.canonical_name = 'gala apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["gala apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_galbani'})
SET i.canonical_name = 'galbani',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["galbanis"],
    i.variations = '{"other": ["galbani"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_garbanzo_bean'})
SET i.canonical_name = 'garbanzo bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["garbanzo beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garbanzo_bean_flour'})
SET i.canonical_name = 'garbanzo bean flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["garbanzo bean flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garbonzo_bean'})
SET i.canonical_name = 'garbonzo bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["garbonzo beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garden_pea'})
SET i.canonical_name = 'garden pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["garden peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic'})
SET i.canonical_name = 'garlic',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["garlics"],
    i.variations = '{"other": ["fried garlic", "garlic", "powdered garlic"], "cut_or_form": ["roasted garlic"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_bread'})
SET i.canonical_name = 'garlic bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["garlic breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_bulb'})
SET i.canonical_name = 'garlic bulb',
    i.category = 'vegetable',
    i.base = 'garlic',
    i.alt_names = ["garlic bulbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_chili_sauce'})
SET i.canonical_name = 'garlic chili sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["garlic chili sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_chive'})
SET i.canonical_name = 'garlic chive',
    i.category = 'herb',
    i.base = 'chive',
    i.alt_names = ["garlic chives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_clove'})
SET i.canonical_name = 'garlic clove',
    i.category = 'seasoning',
    i.base = 'clove',
    i.alt_names = ["garlic cloves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_flak'})
SET i.canonical_name = 'garlic flak',
    i.category = 'vegetable',
    i.base = 'garlic',
    i.alt_names = ["garlic flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_herb_feta'})
SET i.canonical_name = 'garlic herb feta',
    i.category = 'dairy',
    i.base = 'feta',
    i.alt_names = ["garlic herb fetas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_herb_spreadable_cheese'})
SET i.canonical_name = 'garlic herb spreadable cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["garlic herb spreadable cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_juice'})
SET i.canonical_name = 'garlic juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["garlic juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_mayonnaise'})
SET i.canonical_name = 'garlic mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["garlic mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_naan'})
SET i.canonical_name = 'garlic naan',
    i.category = 'grain',
    i.base = 'naan',
    i.alt_names = ["garlic naans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_oil'})
SET i.canonical_name = 'garlic oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["garlic oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_olive_oil'})
SET i.canonical_name = 'garlic olive oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["garlic olive oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_pepper_blend'})
SET i.canonical_name = 'garlic pepper blend',
    i.category = 'vegetable',
    i.base = 'garlic',
    i.alt_names = ["garlic pepper blends"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_powder'})
SET i.canonical_name = 'garlic powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["garlic powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_puree'})
SET i.canonical_name = 'garlic puree',
    i.category = 'condiment',
    i.base = 'puree',
    i.alt_names = ["garlic purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_salt'})
SET i.canonical_name = 'garlic salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["garlic salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_sauce'})
SET i.canonical_name = 'garlic sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["garlic sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_garlic_shoot'})
SET i.canonical_name = 'garlic shoot',
    i.category = 'vegetable',
    i.base = 'shoot',
    i.alt_names = ["garlic shoots"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gebhardt_chili_powder'})
SET i.canonical_name = 'gebhardt chili powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["gebhardt chili powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ghee'})
SET i.canonical_name = 'ghee',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["ghees"],
    i.variations = '{"other": ["ghee"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_giant_white_bean'})
SET i.canonical_name = 'giant white bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["giant white beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_giardiniera'})
SET i.canonical_name = 'giardiniera',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["giardinieras"],
    i.variations = '{"other": ["giardiniera"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ginger'})
SET i.canonical_name = 'ginger',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["gingers"],
    i.variations = '{"other": ["ginger", "ginger purée", "ginger root"], "cut_or_form": ["fresh ginger", "ground ginger"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_ale'})
SET i.canonical_name = 'ginger ale',
    i.category = 'beverage',
    i.base = 'ale',
    i.alt_names = ["ginger ales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_beer'})
SET i.canonical_name = 'ginger beer',
    i.category = 'beverage',
    i.base = 'beer',
    i.alt_names = ["ginger beers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_juice'})
SET i.canonical_name = 'ginger juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["ginger juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_liqueur'})
SET i.canonical_name = 'ginger liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["ginger liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_paste'})
SET i.canonical_name = 'ginger paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["ginger pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_piece'})
SET i.canonical_name = 'ginger piece',
    i.category = 'seasoning',
    i.base = 'ginger',
    i.alt_names = ["ginger pieces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ginger_syrup'})
SET i.canonical_name = 'ginger syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["ginger syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gingersnap_cookie_crumb'})
SET i.canonical_name = 'gingersnap cookie crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["gingersnap cookie crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gingersnap_crumb'})
SET i.canonical_name = 'gingersnap crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["gingersnap crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_glace_cherry'})
SET i.canonical_name = 'glace cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["glace cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_glaze'})
SET i.canonical_name = 'glaze',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["glazes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_globe_eggplant'})
SET i.canonical_name = 'globe eggplant',
    i.category = 'vegetable',
    i.base = 'eggplant',
    i.alt_names = ["globe eggplants"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_glucose_syrup'})
SET i.canonical_name = 'glucose syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["glucose syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten'})
SET i.canonical_name = 'gluten',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["glutens"],
    i.variations = '{"other": ["gluten"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_flour'})
SET i.canonical_name = 'gluten flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["gluten flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_barbecue_sauce'})
SET i.canonical_name = 'gluten free barbecue sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["gluten free barbecue sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_blend'})
SET i.canonical_name = 'gluten free blend',
    i.category = 'grain',
    i.base = 'gluten',
    i.alt_names = ["gluten free blends"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_chicken_broth'})
SET i.canonical_name = 'gluten free chicken broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["gluten free chicken broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_corn_tortilla'})
SET i.canonical_name = 'gluten free corn tortilla',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["gluten free corn tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_cornmeal'})
SET i.canonical_name = 'gluten free cornmeal',
    i.category = 'grain',
    i.base = 'cornmeal',
    i.alt_names = ["gluten free cornmeals"],
    i.variations = null;

// Progress: 900/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_lasagna_noodle'})
SET i.canonical_name = 'gluten free lasagna noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["gluten free lasagna noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_marinara_sauce'})
SET i.canonical_name = 'gluten free marinara sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["gluten free marinara sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_rice_chex'})
SET i.canonical_name = 'gluten free rice chex',
    i.category = 'grain',
    i.base = 'gluten',
    i.alt_names = ["gluten free rice chexes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_bread'})
SET i.canonical_name = 'gluten-free bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["gluten-free breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_breadcrumb'})
SET i.canonical_name = 'gluten-free breadcrumb',
    i.category = 'grain',
    i.base = 'breadcrumb',
    i.alt_names = ["gluten-free breadcrumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_broth'})
SET i.canonical_name = 'gluten-free broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["gluten-free broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_chicken_stock'})
SET i.canonical_name = 'gluten-free chicken stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["gluten-free chicken stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_flour'})
SET i.canonical_name = 'gluten-free flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["gluten-free flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_hoisin_sauce'})
SET i.canonical_name = 'gluten-free hoisin sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["gluten-free hoisin sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_oat'})
SET i.canonical_name = 'gluten-free oat',
    i.category = 'grain',
    i.base = 'oat',
    i.alt_names = ["gluten-free oats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_oyster_sauce'})
SET i.canonical_name = 'gluten-free oyster sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["gluten-free oyster sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_pasta'})
SET i.canonical_name = 'gluten-free pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["gluten-free pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_penne'})
SET i.canonical_name = 'gluten-free penne',
    i.category = 'grain',
    i.base = 'penne',
    i.alt_names = ["gluten-free pennes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_pie_crust'})
SET i.canonical_name = 'gluten-free pie crust',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["gluten-free pie crusts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_pizza_crust'})
SET i.canonical_name = 'gluten-free pizza crust',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["gluten-free pizza crusts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_rolled_oats'})
SET i.canonical_name = 'gluten-free rolled oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_spaghetti'})
SET i.canonical_name = 'gluten-free spaghetti',
    i.category = 'grain',
    i.base = 'spaghetti',
    i.alt_names = ["gluten-free spaghettis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_tamari'})
SET i.canonical_name = 'gluten-free tamari',
    i.category = 'condiment',
    i.base = 'tamari',
    i.alt_names = ["gluten-free tamaris"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gluten_free_tamari_sauce'})
SET i.canonical_name = 'gluten-free tamari sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["gluten-free tamari sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_glutinous_rice'})
SET i.canonical_name = 'glutinous rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["glutinous rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_glutinous_rice_flour'})
SET i.canonical_name = 'glutinous rice flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["glutinous rice flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gnocchi'})
SET i.canonical_name = 'gnocchi',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["gnocchis"],
    i.variations = '{"other": ["gnocchi"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_goat'})
SET i.canonical_name = 'goat',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["goats"],
    i.variations = '{"other": ["baby goat", "goat"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_goat_cheese'})
SET i.canonical_name = 'goat cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["goat cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_goat_milk_feta'})
SET i.canonical_name = 'goat milk feta',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["goat milk fetas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_goat_s_milk_cheese'})
SET i.canonical_name = 'goat s milk cheese',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["goat s milk cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gochujang'})
SET i.canonical_name = 'gochujang',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["gochujangs"],
    i.variations = '{"other": ["gochujang"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_godiva_chocolate_liqueur'})
SET i.canonical_name = 'godiva chocolate liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["godiva chocolate liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_goji_berry'})
SET i.canonical_name = 'goji berry',
    i.category = 'fruit',
    i.base = 'berry',
    i.alt_names = ["goji berries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gold_medal_flour'})
SET i.canonical_name = 'gold medal flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["gold medal flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_goose'})
SET i.canonical_name = 'goose',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["gooses"],
    i.variations = '{"other": ["goose"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_goose_liver'})
SET i.canonical_name = 'goose liver',
    i.category = 'meat',
    i.base = 'goose',
    i.alt_names = ["goose livers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gorgonzola'})
SET i.canonical_name = 'gorgonzola',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["gorgonzolas"],
    i.variations = '{"other": ["gorgonzola"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_gouda'})
SET i.canonical_name = 'gouda',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["goudas"],
    i.variations = '{"other": ["gouda"], "cut_or_form": ["smoked gouda"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_goya_corn_oil'})
SET i.canonical_name = 'goya corn oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["goya corn oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_goya_hot_sauce'})
SET i.canonical_name = 'goya hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["goya hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grain'})
SET i.canonical_name = 'grain',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["grains"],
    i.variations = '{"other": ["grain"], "cut_or_form": ["whole grain bun"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_gram_flour'})
SET i.canonical_name = 'gram flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["gram flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_granary_bread'})
SET i.canonical_name = 'granary bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["granary breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_granny_smith_apple'})
SET i.canonical_name = 'granny smith apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["granny smith apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_granola'})
SET i.canonical_name = 'granola',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["granolas"],
    i.variations = '{"other": ["granola"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_granulated_garlic'})
SET i.canonical_name = 'granulated garlic',
    i.category = 'vegetable',
    i.base = 'garlic',
    i.alt_names = ["granulated garlics"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_granulated_sugar'})
SET i.canonical_name = 'granulated sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["granulated sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_granulated_white_sugar'})
SET i.canonical_name = 'granulated white sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["granulated white sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grap'})
SET i.canonical_name = 'grap',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["graps"],
    i.variations = '{"other": ["grap"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_grape'})
SET i.canonical_name = 'grape',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["grapes"],
    i.variations = '{"other": ["grape"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_grape_juice'})
SET i.canonical_name = 'grape juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["grape juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grape_leaf'})
SET i.canonical_name = 'grape leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["grape leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grape_tomato'})
SET i.canonical_name = 'grape tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["grape tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grape_vine_leaf'})
SET i.canonical_name = 'grape vine leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["grape vine leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grapefruit'})
SET i.canonical_name = 'grapefruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["grapefruits"],
    i.variations = '{"other": ["grapefruit"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_grapefruit_juice'})
SET i.canonical_name = 'grapefruit juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["grapefruit juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grapeseed_oil'})
SET i.canonical_name = 'grapeseed oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["grapeseed oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grassfed_beef'})
SET i.canonical_name = 'grassfed beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["grassfed beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grating_cheese'})
SET i.canonical_name = 'grating cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["grating cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gravenstein_apple'})
SET i.canonical_name = 'gravenstein apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["gravenstein apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gravy'})
SET i.canonical_name = 'gravy',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["gravies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_gray_salt'})
SET i.canonical_name = 'gray salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["gray salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_great_northern_bean'})
SET i.canonical_name = 'great northern bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["great northern beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green'})
SET i.canonical_name = 'green',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["greens"],
    i.variations = '{"variety": ["baby green", "scallion green", "spring green"], "cut_or_form": ["whole green peperoncini"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_green_apple'})
SET i.canonical_name = 'green apple',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green apples", "greenapple", "greenapples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_bean'})
SET i.canonical_name = 'green bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["green beans", "greenbean", "greenbeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_bellpepper'})
SET i.canonical_name = 'green bellpepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green bellpeppers", "greenbellpepper", "greenbellpeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_cabbage'})
SET i.canonical_name = 'green cabbage',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green cabbages", "greencabbage", "greencabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_cardamom'})
SET i.canonical_name = 'green cardamom',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["green cardamoms", "greencardamom", "greencardamoms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_cardamom_pod'})
SET i.canonical_name = 'green cardamom pod',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["green cardamom pods", "greencardamompod", "greencardamompods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_cauliflower'})
SET i.canonical_name = 'green cauliflower',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green cauliflowers", "greencauliflower", "greencauliflowers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_chard'})
SET i.canonical_name = 'green chard',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green chards", "greenchard", "greenchards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_curry_paste'})
SET i.canonical_name = 'green curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["green curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_enchilada_sauce'})
SET i.canonical_name = 'green enchilada sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["green enchilada sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_fig'})
SET i.canonical_name = 'green fig',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green figs", "greenfig", "greenfigs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_garlic'})
SET i.canonical_name = 'green garlic',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green garlics", "greengarlic", "greengarlics"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_gram'})
SET i.canonical_name = 'green gram',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green grams", "greengram", "greengrams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_grape'})
SET i.canonical_name = 'green grape',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green grapes", "greengrape", "greengrapes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_leaf_lettuce'})
SET i.canonical_name = 'green leaf lettuce',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["green leaf lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_lentil'})
SET i.canonical_name = 'green lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["green lentils", "greenlentil", "greenlentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_mango'})
SET i.canonical_name = 'green mango',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green mangos", "greenmango", "greenmangos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_olive'})
SET i.canonical_name = 'green olive',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green olives", "greenolive", "greenolives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_onion'})
SET i.canonical_name = 'green onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green onions", "greenonion", "greenonions", "scallion", "spring onion"],
    i.variations = '{"other": ["green onion bottom"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_green_papaya'})
SET i.canonical_name = 'green papaya',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green papayas", "greenpapaya", "greenpapayas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_pea'})
SET i.canonical_name = 'green pea',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green peas", "greenpea", "greenpeas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_pepper'})
SET i.canonical_name = 'green pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green peppers", "greenpepper", "greenpeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_peppercorn'})
SET i.canonical_name = 'green peppercorn',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["green peppercorns", "greenpeppercorn", "greenpeppercorns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_pesto'})
SET i.canonical_name = 'green pesto',
    i.category = 'condiment',
    i.base = 'pesto',
    i.alt_names = ["green pestos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_plantain'})
SET i.canonical_name = 'green plantain',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["green plantains", "greenplantain", "greenplantains"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_soybean'})
SET i.canonical_name = 'green soybean',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green soybeans", "greensoybean", "greensoybeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_split_pea'})
SET i.canonical_name = 'green split pea',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green split peas", "greensplitpea", "greensplitpeas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_tea'})
SET i.canonical_name = 'green tea',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["green teas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_tea_bag'})
SET i.canonical_name = 'green tea bag',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["green tea bags"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_tea_leaf'})
SET i.canonical_name = 'green tea leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["green tea leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_tea_powder'})
SET i.canonical_name = 'green tea powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["green tea powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_tomato'})
SET i.canonical_name = 'green tomato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["green tomatos", "greentomato", "greentomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_green_tomato_relish'})
SET i.canonical_name = 'green tomato relish',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["green tomato relishes", "greentomatorelish", "greentomatorelishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grenadine_syrup'})
SET i.canonical_name = 'grenadine syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["grenadine syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grey_poupon_dijon_mustard'})
SET i.canonical_name = 'grey poupon dijon mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["grey poupon dijon mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_grigio'})
SET i.canonical_name = 'grigio',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["grigios"],
    i.variations = '{"other": ["grigio"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_gruyere_cheese'})
SET i.canonical_name = 'gruyere cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["gruyere cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_guacamole'})
SET i.canonical_name = 'guacamole',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["guacamoles"],
    i.variations = '{"other": ["guacamole"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_guava'})
SET i.canonical_name = 'guava',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["guavas"],
    i.variations = '{"other": ["guava"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_guinea_hen'})
SET i.canonical_name = 'guinea hen',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["guinea hens", "guineahen", "guineahens"],
    i.variations = '{"other": ["guinea hen"]}';

// Progress: 1000/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_guinness_beer'})
SET i.canonical_name = 'guinness beer',
    i.category = 'beverage',
    i.base = 'beer',
    i.alt_names = ["guinness beers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_habanero_hot_sauce'})
SET i.canonical_name = 'habanero hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["habanero hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_habanero_pepper'})
SET i.canonical_name = 'habanero pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["habanero peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_habanero_powder'})
SET i.canonical_name = 'habanero powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["habanero powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_haddock'})
SET i.canonical_name = 'haddock',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["haddocks"],
    i.variations = '{"other": ["haddock"], "cut_or_form": ["skinless haddock", "smoked haddock"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_haddock_fillet'})
SET i.canonical_name = 'haddock fillet',
    i.category = 'seafood',
    i.base = 'haddock',
    i.alt_names = ["haddock fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_halloumi_cheese'})
SET i.canonical_name = 'halloumi cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["halloumi cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ham'})
SET i.canonical_name = 'ham',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["hams"],
    i.variations = '{"product": ["ham"], "cut_or_form": ["smoked ham", "smoked ham hock"], "nutrition": ["reduced sodium smoked ham"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_hanout'})
SET i.canonical_name = 'hanout',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["hanouts"],
    i.variations = '{"other": ["hanout"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_hard_cheese'})
SET i.canonical_name = 'hard cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["hard cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_haricot_bean'})
SET i.canonical_name = 'haricot bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["haricot beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_harissa_paste'})
SET i.canonical_name = 'harissa paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["harissa pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_harissa_sauce'})
SET i.canonical_name = 'harissa sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["harissa sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hash_brown'})
SET i.canonical_name = 'hash brown',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["hash browns", "hashbrown", "hashbrowns"],
    i.variations = '{"other": ["hash brown"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_hass_avocado'})
SET i.canonical_name = 'hass avocado',
    i.category = 'fruit',
    i.base = 'avocado',
    i.alt_names = ["hass avocados"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hatch_green_chile'})
SET i.canonical_name = 'hatch green chile',
    i.category = 'seasoning',
    i.base = 'chile',
    i.alt_names = ["hatch green chiles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_havarti_cheese'})
SET i.canonical_name = 'havarti cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["havarti cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hawaiian_salt'})
SET i.canonical_name = 'hawaiian salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["hawaiian salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hazelnut_butter'})
SET i.canonical_name = 'hazelnut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["hazelnut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hazelnut_flour'})
SET i.canonical_name = 'hazelnut flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["hazelnut flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hazelnut_liqueur'})
SET i.canonical_name = 'hazelnut liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["hazelnut liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hazelnut_oil'})
SET i.canonical_name = 'hazelnut oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["hazelnut oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hazelnut_paste'})
SET i.canonical_name = 'hazelnut paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["hazelnut pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_head_cauliflower'})
SET i.canonical_name = 'head cauliflower',
    i.category = 'vegetable',
    i.base = 'cauliflower',
    i.alt_names = ["head cauliflowers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_heavy_cream'})
SET i.canonical_name = 'heavy cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["heavy creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_heavy_whipping_cream'})
SET i.canonical_name = 'heavy whipping cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["heavy whipping creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_heirloom_tomato'})
SET i.canonical_name = 'heirloom tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["heirloom tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herb_cheese'})
SET i.canonical_name = 'herb cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["herb cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herb_sauce'})
SET i.canonical_name = 'herb sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["herb sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herb_vinegar'})
SET i.canonical_name = 'herb vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["herb vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herbed_goat_cheese'})
SET i.canonical_name = 'herbed goat cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["herbed goat cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herdez_salsa'})
SET i.canonical_name = 'herdez salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["herdez salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herdez_salsa_casera'})
SET i.canonical_name = 'herdez salsa casera',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["herdez salsa caseras"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_herdez_salsa_verde'})
SET i.canonical_name = 'herdez salsa verde',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["herdez salsa verdes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_high_gluten_bread_flour'})
SET i.canonical_name = 'high gluten bread flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["high gluten bread flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_high_fructose_corn_syrup'})
SET i.canonical_name = 'high-fructose corn syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["high-fructose corn syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_high_gluten_flour'})
SET i.canonical_name = 'high-gluten flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["high-gluten flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_himalayan_salt'})
SET i.canonical_name = 'himalayan salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["himalayan salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hog_jowl'})
SET i.canonical_name = 'hog jowl',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["hog jowls", "hogjowl", "hogjowls"],
    i.variations = '{"other": ["hog jowl"], "cut_or_form": ["smoked hog jowl"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_hoisin_sauce'})
SET i.canonical_name = 'hoisin sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["hoisin sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hoja_santa_leaf'})
SET i.canonical_name = 'hoja santa leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["hoja santa leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hollandaise_sauce'})
SET i.canonical_name = 'hollandaise sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["hollandaise sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_honey'})
SET i.canonical_name = 'honey',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["honeies"],
    i.variations = '{"other": ["honey", "raw honey"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_honey_dijon_mustard'})
SET i.canonical_name = 'honey dijon mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["honey dijon mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_honey_glazed_ham'})
SET i.canonical_name = 'honey glazed ham',
    i.category = 'meat',
    i.base = 'ham',
    i.alt_names = ["honey glazed hams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_honey_gold_potato'})
SET i.canonical_name = 'honey gold potato',
    i.category = 'vegetable',
    i.base = 'potato',
    i.alt_names = ["honey gold potatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_honey_liqueur'})
SET i.canonical_name = 'honey liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["honey liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_honey_mustard'})
SET i.canonical_name = 'honey mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["honey mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_honey_whiskey'})
SET i.canonical_name = 'honey whiskey',
    i.category = 'beverage',
    i.base = 'whiskey',
    i.alt_names = ["honey whiskeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hoop_cheese'})
SET i.canonical_name = 'hoop cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["hoop cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_horseradish'})
SET i.canonical_name = 'horseradish',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["horse radish", "horse radishes", "horseradishes"],
    i.variations = '{"other": ["creamed horseradish", "horseradish", "horseradish root", "prepared horseradish"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_horseradish_cream'})
SET i.canonical_name = 'horseradish cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["horseradish creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_horseradish_mustard'})
SET i.canonical_name = 'horseradish mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["horseradish mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_horseradish_sauce'})
SET i.canonical_name = 'horseradish sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["horseradish sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_bean_paste'})
SET i.canonical_name = 'hot bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["hot bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_cherry_pepper'})
SET i.canonical_name = 'hot cherry pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["hot cherry peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_chili_oil'})
SET i.canonical_name = 'hot chili oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["hot chili oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_chili_paste'})
SET i.canonical_name = 'hot chili paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["hot chili pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_chili_powder'})
SET i.canonical_name = 'hot chili powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["hot chili powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_chili_sauce'})
SET i.canonical_name = 'hot chili sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["hot chili sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_curry_powder'})
SET i.canonical_name = 'hot curry powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["hot curry powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_dog'})
SET i.canonical_name = 'hot dog',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["hot dogs", "hotdog", "hotdogs"],
    i.variations = '{"product": ["hot dog"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_hot_mustard'})
SET i.canonical_name = 'hot mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["hot mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_pepper'})
SET i.canonical_name = 'hot pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["hot peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_pepper_sauce'})
SET i.canonical_name = 'hot pepper sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["hot pepper sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_pork_sausage'})
SET i.canonical_name = 'hot pork sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["hot pork sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_red_pepper_flak'})
SET i.canonical_name = 'hot red pepper flak',
    i.category = 'seafood',
    i.base = 'red',
    i.alt_names = ["hot red pepper flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_salsa'})
SET i.canonical_name = 'hot salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["hot salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_hot_sauce'})
SET i.canonical_name = 'hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ibarra_chocolate'})
SET i.canonical_name = 'ibarra chocolate',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["ibarra chocolates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ice_cream'})
SET i.canonical_name = 'ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ice_cream_salt'})
SET i.canonical_name = 'ice cream salt',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["ice cream salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_iceberg_lettuce'})
SET i.canonical_name = 'iceberg lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["iceberg lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_iodized_salt'})
SET i.canonical_name = 'iodized salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["iodized salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_irish_cream_liqueur'})
SET i.canonical_name = 'irish cream liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["irish cream liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_irish_oats'})
SET i.canonical_name = 'irish oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_irish_red_ale'})
SET i.canonical_name = 'irish red ale',
    i.category = 'beverage',
    i.base = 'ale',
    i.alt_names = ["irish red ales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jack_cheese'})
SET i.canonical_name = 'jack cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["jack cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jackfruit'})
SET i.canonical_name = 'jackfruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["jackfruits"],
    i.variations = '{"other": ["jackfruit"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_jagermeister_liqueur'})
SET i.canonical_name = 'jagermeister liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["jagermeister liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jam'})
SET i.canonical_name = 'jam',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jamaican_curry_powder'})
SET i.canonical_name = 'jamaican curry powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["jamaican curry powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jamaican_jerk_marinade'})
SET i.canonical_name = 'jamaican jerk marinade',
    i.category = 'condiment',
    i.base = 'marinade',
    i.alt_names = ["jamaican jerk marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jamaican_jerk_spice'})
SET i.canonical_name = 'jamaican jerk spice',
    i.category = 'seasoning',
    i.base = 'spice',
    i.alt_names = ["jamaican jerk spices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jasmine_brown_rice'})
SET i.canonical_name = 'jasmine brown rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["jasmine brown rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jasmine_rice'})
SET i.canonical_name = 'jasmine rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["jasmine rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jerk_marinade'})
SET i.canonical_name = 'jerk marinade',
    i.category = 'condiment',
    i.base = 'marinade',
    i.alt_names = ["jerk marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jerk_paste'})
SET i.canonical_name = 'jerk paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["jerk pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jerk_sauce'})
SET i.canonical_name = 'jerk sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["jerk sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jerusalem_artichok'})
SET i.canonical_name = 'jerusalem artichok',
    i.category = 'vegetable',
    i.base = 'artichok',
    i.alt_names = ["jerusalem artichoks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jimmy_dean_pork_sausage'})
SET i.canonical_name = 'jimmy dean pork sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["jimmy dean pork sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_juice'})
SET i.canonical_name = 'juice',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["juices"],
    i.variations = '{"other": ["bottled clam juice", "bottled lime juice"], "cut_or_form": ["fresh lemon juice", "fresh lime juice", "fresh orange juice"], "nutrition": ["low sodium tomato juice", "reduced sodium tomato juice"], "flavor_source": ["low sodium vegetable juice", "reduced sodium vegetable juice"], "grade_style": ["sweet pickle juice", "unsweetened apple juice", "unsweetened pineapple juice"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_juice_concentrate'})
SET i.canonical_name = 'juice concentrate',
    i.category = 'condiment',
    i.base = 'concentrate',
    i.alt_names = ["juice concentrates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jumbo_macaroni_shell'})
SET i.canonical_name = 'jumbo macaroni shell',
    i.category = 'grain',
    i.base = 'macaroni',
    i.alt_names = ["jumbo macaroni shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jumbo_pasta_shell'})
SET i.canonical_name = 'jumbo pasta shell',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["jumbo pasta shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_jumbo_shrimp'})
SET i.canonical_name = 'jumbo shrimp',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["jumbo shrimps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kaffir_lime'})
SET i.canonical_name = 'kaffir lime',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["kaffir limes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kaffir_lime_leaf'})
SET i.canonical_name = 'kaffir lime leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["kaffir lime leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kahlua_liqueur'})
SET i.canonical_name = 'kahlua liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["kahlua liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kalamansi_juice'})
SET i.canonical_name = 'kalamansi juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["kalamansi juices"],
    i.variations = null;

// Progress: 1100/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_kalamata'})
SET i.canonical_name = 'kalamata',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["kalamatas"],
    i.variations = '{"other": ["kalamata"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kale'})
SET i.canonical_name = 'kale',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["kales"],
    i.variations = '{"other": ["baby kale", "kale"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kale_leaf'})
SET i.canonical_name = 'kale leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["kale leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kamut_flour'})
SET i.canonical_name = 'kamut flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["kamut flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_karo_corn_syrup'})
SET i.canonical_name = 'karo corn syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["karo corn syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_karo_syrup'})
SET i.canonical_name = 'karo syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["karo syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_katsuobushi'})
SET i.canonical_name = 'katsuobushi',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["katsuobushis"],
    i.variations = '{"other": ["katsuobushi"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kelp'})
SET i.canonical_name = 'kelp',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["kelps"],
    i.variations = '{"other": ["kelp"], "cut_or_form": ["dried kelp"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kernel'})
SET i.canonical_name = 'kernel',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["kernels"],
    i.variations = '{"other": ["kernel"], "grade_style": ["sweet corn kernel"], "cut_or_form": ["frozen corn kernel", "whole kernel corn, drain"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ketchup'})
SET i.canonical_name = 'ketchup',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["ketchups"],
    i.variations = '{"nutrition": ["no salt added ketchup", "reduced sugar ketchup"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kettle_chip'})
SET i.canonical_name = 'kettle chip',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["kettle chips", "kettlechip", "kettlechips"],
    i.variations = '{"other": ["kettle chip"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kewpie_mayonnaise'})
SET i.canonical_name = 'kewpie mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["kewpie mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_key_lime'})
SET i.canonical_name = 'key lime',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["key limes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_key_lime_juice'})
SET i.canonical_name = 'key lime juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["key lime juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kidney'})
SET i.canonical_name = 'kidney',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["kidneies"],
    i.variations = '{"other": ["kidney"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kidney_bean'})
SET i.canonical_name = 'kidney bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["kidney beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kielbasa'})
SET i.canonical_name = 'kielbasa',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["kielbasas"],
    i.variations = '{"other": ["kielbasa"], "cut_or_form": ["smoked kielbasa"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kimchi_juice'})
SET i.canonical_name = 'kimchi juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["kimchi juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_king_crab'})
SET i.canonical_name = 'king crab',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["king crabs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_king_crab_leg'})
SET i.canonical_name = 'king crab leg',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["king crab legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_king_oyster_mushroom'})
SET i.canonical_name = 'king oyster mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["king oyster mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_king_salmon'})
SET i.canonical_name = 'king salmon',
    i.category = 'seafood',
    i.base = 'salmon',
    i.alt_names = ["king salmons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kiwi'})
SET i.canonical_name = 'kiwi',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["kiwis"],
    i.variations = '{"other": ["kiwi"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kiwi_fruit'})
SET i.canonical_name = 'kiwi fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["kiwi fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kohlrabi'})
SET i.canonical_name = 'kohlrabi',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["kohlrabis"],
    i.variations = '{"other": ["kohlrabi"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_korma_paste'})
SET i.canonical_name = 'korma paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["korma pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kosher_salt'})
SET i.canonical_name = 'kosher salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["kosher salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kosher_wine'})
SET i.canonical_name = 'kosher wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["kosher wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_kraut'})
SET i.canonical_name = 'kraut',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["krauts"],
    i.variations = '{"other": ["kraut"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_kung_pao_sauce'})
SET i.canonical_name = 'kung pao sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["kung pao sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_labneh'})
SET i.canonical_name = 'labneh',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["labnehs"],
    i.variations = '{"other": ["labneh"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lacinato_kale'})
SET i.canonical_name = 'lacinato kale',
    i.category = 'vegetable',
    i.base = 'kale',
    i.alt_names = ["lacinato kales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lady_apple'})
SET i.canonical_name = 'lady apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["lady apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lager_beer'})
SET i.canonical_name = 'lager beer',
    i.category = 'beverage',
    i.base = 'beer',
    i.alt_names = ["lager beers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_laksa_paste'})
SET i.canonical_name = 'laksa paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["laksa pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb'})
SET i.canonical_name = 'lamb',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["lambs"],
    i.variations = '{"other": ["lamb"], "cut_or_form": ["boneless lamb", "ground lamb"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_breast'})
SET i.canonical_name = 'lamb breast',
    i.category = 'meat',
    i.base = 'breast',
    i.alt_names = ["lamb breasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_chop'})
SET i.canonical_name = 'lamb chop',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_cub'})
SET i.canonical_name = 'lamb cub',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb cubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_cutlet'})
SET i.canonical_name = 'lamb cutlet',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb cutlets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_fillet'})
SET i.canonical_name = 'lamb fillet',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_kidney'})
SET i.canonical_name = 'lamb kidney',
    i.category = 'plant_protein',
    i.base = 'kidney',
    i.alt_names = ["lamb kidneies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_leg'})
SET i.canonical_name = 'lamb leg',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_leg_steak'})
SET i.canonical_name = 'lamb leg steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["lamb leg steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_loin'})
SET i.canonical_name = 'lamb loin',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb loins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_loin_chop'})
SET i.canonical_name = 'lamb loin chop',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb loin chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_neck'})
SET i.canonical_name = 'lamb neck',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb necks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_neck_fillet'})
SET i.canonical_name = 'lamb neck fillet',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb neck fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_rack'})
SET i.canonical_name = 'lamb rack',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb racks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_rib_chop'})
SET i.canonical_name = 'lamb rib chop',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb rib chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_rib_roast'})
SET i.canonical_name = 'lamb rib roast',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb rib roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_sausage'})
SET i.canonical_name = 'lamb sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["lamb sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_shank'})
SET i.canonical_name = 'lamb shank',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb shanks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_shoulder'})
SET i.canonical_name = 'lamb shoulder',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb shoulders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_shoulder_chop'})
SET i.canonical_name = 'lamb shoulder chop',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb shoulder chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_steak'})
SET i.canonical_name = 'lamb steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["lamb steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_stew_meat'})
SET i.canonical_name = 'lamb stew meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["lamb stew meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_stock'})
SET i.canonical_name = 'lamb stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["lamb stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lamb_strip'})
SET i.canonical_name = 'lamb strip',
    i.category = 'meat',
    i.base = 'lamb',
    i.alt_names = ["lamb strips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lasagna'})
SET i.canonical_name = 'lasagna',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["lasagnas"],
    i.variations = '{"other": ["dreamfields lasagna", "dry lasagna", "lasagna", "uncooked lasagna"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lasagna_noodle'})
SET i.canonical_name = 'lasagna noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["lasagna noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lasagna_sheet'})
SET i.canonical_name = 'lasagna sheet',
    i.category = 'grain',
    i.base = 'lasagna',
    i.alt_names = ["lasagna sheets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_laurel_leaf'})
SET i.canonical_name = 'laurel leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["laurel leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lavender'})
SET i.canonical_name = 'lavender',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["lavenders"],
    i.variations = '{"other": ["lavender"], "cut_or_form": ["dried lavender", "dried lavender flower"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lavender_honey'})
SET i.canonical_name = 'lavender honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["lavender honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_leaf'})
SET i.canonical_name = 'leaf',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["leafes", "leafs", "leaves"],
    i.variations = '{"other": ["baby leaf lettuce", "baby spinach leaf", "oregano leaf", "spice islands bay leaf"], "cut_or_form": ["basil dried leaf", "dried cilantro leaf", "dried neem leaf", "dried tarragon leaf", "fresh basil leaf", "fresh bay leaf", "fresh curry leaf", "fresh oregano leaf", "fresh parsley leaf", "fresh thyme leaf", "frozen banana leaf"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_leaf_lettuce'})
SET i.canonical_name = 'leaf lettuce',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["leaf lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_leaf_parsley'})
SET i.canonical_name = 'leaf parsley',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["leaf parsleies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lean_beef'})
SET i.canonical_name = 'lean beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["lean beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lean_meat'})
SET i.canonical_name = 'lean meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["lean meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_leaves'})
SET i.canonical_name = 'leaves',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["leaveses"],
    i.variations = '{"cut_or_form": ["dried leaves oregano"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_leek'})
SET i.canonical_name = 'leek',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["leeks"],
    i.variations = '{"other": ["leek"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_leek_top'})
SET i.canonical_name = 'leek top',
    i.category = 'vegetable',
    i.base = 'leek',
    i.alt_names = ["leek tops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_leftover_meat'})
SET i.canonical_name = 'leftover meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["leftover meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon'})
SET i.canonical_name = 'lemon',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["lemons"],
    i.variations = '{"other": ["lemon"], "cut_or_form": ["fresh lemon"], "nutrition": ["diet lemon lime soda"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_cucumber'})
SET i.canonical_name = 'lemon cucumber',
    i.category = 'vegetable',
    i.base = 'cucumber',
    i.alt_names = ["lemon cucumbers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_curd'})
SET i.canonical_name = 'lemon curd',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon curds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_gras'})
SET i.canonical_name = 'lemon gras',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_juice'})
SET i.canonical_name = 'lemon juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["lemon juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_lime_beverage'})
SET i.canonical_name = 'lemon lime beverage',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon lime beverages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_olive_oil'})
SET i.canonical_name = 'lemon olive oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["lemon olive oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_peel'})
SET i.canonical_name = 'lemon peel',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon peels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_pepper'})
SET i.canonical_name = 'lemon pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["lemon peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_rind'})
SET i.canonical_name = 'lemon rind',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon rinds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_slice'})
SET i.canonical_name = 'lemon slice',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_soda'})
SET i.canonical_name = 'lemon soda',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon sodas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_thyme'})
SET i.canonical_name = 'lemon thyme',
    i.category = 'herb',
    i.base = 'thyme',
    i.alt_names = ["lemon thymes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_twist'})
SET i.canonical_name = 'lemon twist',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon twists"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_verbena'})
SET i.canonical_name = 'lemon verbena',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon verbenas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_vodka'})
SET i.canonical_name = 'lemon vodka',
    i.category = 'beverage',
    i.base = 'vodka',
    i.alt_names = ["lemon vodkas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_wedge'})
SET i.canonical_name = 'lemon wedge',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon wedges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_zest'})
SET i.canonical_name = 'lemon zest',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["lemon zests"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lemon_lime_soda'})
SET i.canonical_name = 'lemon-lime soda',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["lemon-lime sodas", "lemon-limesoda", "lemon-limesodas"],
    i.variations = '{"other": ["lemon-lime soda"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lemongrass'})
SET i.canonical_name = 'lemongrass',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["lemongrasses"],
    i.variations = '{"other": ["lemongrass"], "cut_or_form": ["ground lemongrass"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lentil'})
SET i.canonical_name = 'lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["lentils"],
    i.variations = '{"other": ["lentil"], "cut_or_form": ["dried lentil"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lettuce'})
SET i.canonical_name = 'lettuce',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["lettuces"],
    i.variations = '{"other": ["baby gem lettuce", "lettuce"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lettuce_heart'})
SET i.canonical_name = 'lettuce heart',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["lettuce hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lettuce_leaf'})
SET i.canonical_name = 'lettuce leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["lettuce leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_levain_bread'})
SET i.canonical_name = 'levain bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["levain breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lima_bean'})
SET i.canonical_name = 'lima bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["lima beans"],
    i.variations = null;

// Progress: 1200/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_lime'})
SET i.canonical_name = 'lime',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["limes"],
    i.variations = '{"other": ["lime"], "cut_or_form": ["fresh lime"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lime_juice'})
SET i.canonical_name = 'lime juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["lime juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lime_leaf'})
SET i.canonical_name = 'lime leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["lime leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lime_peel'})
SET i.canonical_name = 'lime peel',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["lime peels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lime_rind'})
SET i.canonical_name = 'lime rind',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["lime rinds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lime_slice'})
SET i.canonical_name = 'lime slice',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["lime slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lime_wedge'})
SET i.canonical_name = 'lime wedge',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["lime wedges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lime_zest'})
SET i.canonical_name = 'lime zest',
    i.category = 'fruit',
    i.base = 'lime',
    i.alt_names = ["lime zests"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_limoncello'})
SET i.canonical_name = 'limoncello',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["limoncellos"],
    i.variations = '{"other": ["limoncello"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_linguine'})
SET i.canonical_name = 'linguine',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["linguines"],
    i.variations = '{"other": ["linguine"], "cut_or_form": ["whole wheat linguine"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lipton_green_tea_bag'})
SET i.canonical_name = 'lipton green tea bag',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["lipton green tea bags"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_liqueur'})
SET i.canonical_name = 'liqueur',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["liqueurs"],
    i.variations = '{"other": ["southern comfort liqueur", "st germain liqueur"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_liquid_egg_whit'})
SET i.canonical_name = 'liquid egg whit',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["liquid egg whits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_liquid_honey'})
SET i.canonical_name = 'liquid honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["liquid honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lite_coconut_milk'})
SET i.canonical_name = 'lite coconut milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["lite coconut milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_littleneck_clam'})
SET i.canonical_name = 'littleneck clam',
    i.category = 'seafood',
    i.base = 'clam',
    i.alt_names = ["littleneck clams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lo_bok'})
SET i.canonical_name = 'lo bok',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["lo boks", "lobok", "loboks"],
    i.variations = '{"other": ["lo bok"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lobster'})
SET i.canonical_name = 'lobster',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["lobsters"],
    i.variations = '{"other": ["lobster"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_lobster_meat'})
SET i.canonical_name = 'lobster meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["lobster meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lobster_stock'})
SET i.canonical_name = 'lobster stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["lobster stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lobster_tail'})
SET i.canonical_name = 'lobster tail',
    i.category = 'seafood',
    i.base = 'lobster',
    i.alt_names = ["lobster tails"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_loose_black_tea'})
SET i.canonical_name = 'loose black tea',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["loose black teas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_loose_leaf_black_tea'})
SET i.canonical_name = 'loose leaf black tea',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["loose leaf black teas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lotus_leaf'})
SET i.canonical_name = 'lotus leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["lotus leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lotus_seed_paste'})
SET i.canonical_name = 'lotus seed paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["lotus seed pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_louisiana_hot_sauce'})
SET i.canonical_name = 'louisiana hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["louisiana hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_lump_crab_meat'})
SET i.canonical_name = 'lump crab meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["lump crab meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_luncheon_meat'})
SET i.canonical_name = 'luncheon meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["luncheon meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maca_powder'})
SET i.canonical_name = 'maca powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["maca powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_macaroni'})
SET i.canonical_name = 'macaroni',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["macaronis"],
    i.variations = '{"other": ["macaroni"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mackerel'})
SET i.canonical_name = 'mackerel',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["mackerels"],
    i.variations = '{"other": ["mackerel"], "cut_or_form": ["smoked mackerel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mackerel_fillet'})
SET i.canonical_name = 'mackerel fillet',
    i.category = 'seafood',
    i.base = 'mackerel',
    i.alt_names = ["mackerel fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_madeira_wine'})
SET i.canonical_name = 'madeira wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["madeira wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_madras_curry_powder'})
SET i.canonical_name = 'madras curry powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["madras curry powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maida_flour'})
SET i.canonical_name = 'maida flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["maida flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maitake_mushroom'})
SET i.canonical_name = 'maitake mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["maitake mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maldon_sea_salt'})
SET i.canonical_name = 'maldon sea salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["maldon sea salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_malt_powder'})
SET i.canonical_name = 'malt powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["malt powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_malt_syrup'})
SET i.canonical_name = 'malt syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["malt syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_malt_vinegar'})
SET i.canonical_name = 'malt vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["malt vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_manchego_cheese'})
SET i.canonical_name = 'manchego cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["manchego cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mandarin'})
SET i.canonical_name = 'mandarin',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["mandarins"],
    i.variations = '{"other": ["mandarin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mandarin_juice'})
SET i.canonical_name = 'mandarin juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["mandarin juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mandarin_orange'})
SET i.canonical_name = 'mandarin orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["mandarin oranges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mandarin_orange_juice'})
SET i.canonical_name = 'mandarin orange juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["mandarin orange juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mandarin_orange_segment'})
SET i.canonical_name = 'mandarin orange segment',
    i.category = 'fruit',
    i.base = 'mandarin',
    i.alt_names = ["mandarin orange segments"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mandarin_pancak'})
SET i.canonical_name = 'mandarin pancak',
    i.category = 'fruit',
    i.base = 'mandarin',
    i.alt_names = ["mandarin pancaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mango'})
SET i.canonical_name = 'mango',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["mangos"],
    i.variations = '{"other": ["mango"], "cut_or_form": ["cubed mango", "dried mango", "frozen mango"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mango_chutney'})
SET i.canonical_name = 'mango chutney',
    i.category = 'condiment',
    i.base = 'chutney',
    i.alt_names = ["mango chutneies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mango_juice'})
SET i.canonical_name = 'mango juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["mango juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mango_nectar'})
SET i.canonical_name = 'mango nectar',
    i.category = 'fruit',
    i.base = 'mango',
    i.alt_names = ["mango nectars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mango_salsa'})
SET i.canonical_name = 'mango salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["mango salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_manicotti_pasta'})
SET i.canonical_name = 'manicotti pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["manicotti pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_manioc_flour'})
SET i.canonical_name = 'manioc flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["manioc flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_manischewitz_potato_starch'})
SET i.canonical_name = 'manischewitz potato starch',
    i.category = 'grain',
    i.base = 'starch',
    i.alt_names = ["manischewitz potato starches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_manzanilla'})
SET i.canonical_name = 'manzanilla',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["manzanillas"],
    i.variations = '{"other": ["manzanilla"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_manzanilla_olive'})
SET i.canonical_name = 'manzanilla olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["manzanilla olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_manzanilla_sherry'})
SET i.canonical_name = 'manzanilla sherry',
    i.category = 'beverage',
    i.base = 'sherry',
    i.alt_names = ["manzanilla sherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maple_sugar'})
SET i.canonical_name = 'maple sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["maple sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maple_syrup'})
SET i.canonical_name = 'maple syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["maple syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_margarita_salt'})
SET i.canonical_name = 'margarita salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["margarita salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_marinade'})
SET i.canonical_name = 'marinade',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_marinara_sauce'})
SET i.canonical_name = 'marinara sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["marinara sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_marjoram_leaf'})
SET i.canonical_name = 'marjoram leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["marjoram leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_marmalade'})
SET i.canonical_name = 'marmalade',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["marmalades"],
    i.variations = '{"nutrition": ["reduced sugar orange marmalade"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_marsala_wine'})
SET i.canonical_name = 'marsala wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["marsala wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_marshmallow_creme'})
SET i.canonical_name = 'marshmallow creme',
    i.category = 'dairy',
    i.base = 'creme',
    i.alt_names = ["marshmallow cremes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_marshmallow_fluff'})
SET i.canonical_name = 'marshmallow fluff',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["marshmallow flufves", "marshmallowfluff", "marshmallowflufves"],
    i.variations = '{"other": ["marshmallow fluff"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_marshmallow_vodka'})
SET i.canonical_name = 'marshmallow vodka',
    i.category = 'beverage',
    i.base = 'vodka',
    i.alt_names = ["marshmallow vodkas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_masa_dough'})
SET i.canonical_name = 'masa dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["masa doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_masala'})
SET i.canonical_name = 'masala',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["masalas"],
    i.variations = '{"cut_or_form": ["whole garam masala"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mashed_banana'})
SET i.canonical_name = 'mashed banana',
    i.category = 'fruit',
    i.base = 'banana',
    i.alt_names = ["mashed bananas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mashed_cauliflower'})
SET i.canonical_name = 'mashed cauliflower',
    i.category = 'vegetable',
    i.base = 'cauliflower',
    i.alt_names = ["mashed cauliflowers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_massaman_curry_paste'})
SET i.canonical_name = 'massaman curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["massaman curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_matcha_green_tea_powder'})
SET i.canonical_name = 'matcha green tea powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["matcha green tea powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_matsutake_mushroom'})
SET i.canonical_name = 'matsutake mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["matsutake mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_matzo_cake_meal'})
SET i.canonical_name = 'matzo cake meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["matzo cake meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_maui_onion'})
SET i.canonical_name = 'maui onion',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["maui onions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mayonnaise'})
SET i.canonical_name = 'mayonnaise',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["mayonnaises"],
    i.variations = '{"nutrition": ["hellmann\'\'s light mayonnaise", "light mayonnaise", "nonfat mayonnaise"], "other": ["vegan mayonnaise"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mazola_canola_oil'})
SET i.canonical_name = 'mazola canola oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["mazola canola oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mazola_corn_oil'})
SET i.canonical_name = 'mazola corn oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["mazola corn oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mcintosh_apple'})
SET i.canonical_name = 'mcintosh apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["mcintosh apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meal'})
SET i.canonical_name = 'meal',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["meals"],
    i.variations = '{"other": ["flax seed meal"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_meat'})
SET i.canonical_name = 'meat',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["meats"],
    i.variations = '{"other": ["imitation crab meat", "meat", "stir fry beef meat"], "cut_or_form": ["cubed meat", "ground meat", "lean ground meat"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_meat_bon'})
SET i.canonical_name = 'meat bon',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["meat bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_cut'})
SET i.canonical_name = 'meat cut',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["meat cuts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_fat'})
SET i.canonical_name = 'meat fat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["meat fats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_glaze'})
SET i.canonical_name = 'meat glaze',
    i.category = 'condiment',
    i.base = 'glaze',
    i.alt_names = ["meat glazes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_marinade'})
SET i.canonical_name = 'meat marinade',
    i.category = 'condiment',
    i.base = 'marinade',
    i.alt_names = ["meat marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_sauce'})
SET i.canonical_name = 'meat sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["meat sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_stock'})
SET i.canonical_name = 'meat stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["meat stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meat_tenderizer'})
SET i.canonical_name = 'meat tenderizer',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["meat tenderizers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meatball'})
SET i.canonical_name = 'meatball',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["meatballs"],
    i.variations = '{"other": ["meatball"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_medjool_date'})
SET i.canonical_name = 'medjool date',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["medjool dates", "medjooldate", "medjooldates"],
    i.variations = '{"other": ["medjool date"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mellow_white_miso'})
SET i.canonical_name = 'mellow white miso',
    i.category = 'condiment',
    i.base = 'miso',
    i.alt_names = ["mellow white misos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_melon_liqueur'})
SET i.canonical_name = 'melon liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["melon liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_melted_butter'})
SET i.canonical_name = 'melted butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["melted butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meringue_powder'})
SET i.canonical_name = 'meringue powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["meringue powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_merlot'})
SET i.canonical_name = 'merlot',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["merlots"],
    i.variations = '{"other": ["merlot"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_methi_leaf'})
SET i.canonical_name = 'methi leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["methi leafs"],
    i.variations = null;

// Progress: 1300/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_meyer_lemon'})
SET i.canonical_name = 'meyer lemon',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["meyer lemons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meyer_lemon_juice'})
SET i.canonical_name = 'meyer lemon juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["meyer lemon juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_meyer_lemon_peel'})
SET i.canonical_name = 'meyer lemon peel',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["meyer lemon peels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_cheddar_cheese'})
SET i.canonical_name = 'mild cheddar cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["mild cheddar cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_curry_paste'})
SET i.canonical_name = 'mild curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["mild curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_curry_powder'})
SET i.canonical_name = 'mild curry powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["mild curry powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_green_chile'})
SET i.canonical_name = 'mild green chile',
    i.category = 'seasoning',
    i.base = 'chile',
    i.alt_names = ["mild green chiles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_olive_oil'})
SET i.canonical_name = 'mild olive oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["mild olive oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_pork_sausage'})
SET i.canonical_name = 'mild pork sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["mild pork sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_salsa'})
SET i.canonical_name = 'mild salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["mild salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mild_white_fish'})
SET i.canonical_name = 'mild white fish',
    i.category = 'seafood',
    i.base = 'fish',
    i.alt_names = ["mild white fishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_milk'})
SET i.canonical_name = 'milk',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["milks"],
    i.variations = '{"other": ["powdered milk", "raw milk"], "cut_or_form": ["canned coconut milk", "whole milk", "whole milk ricotta cheese", "whole milk yoghurt"], "nutrition": ["evaporated skim milk", "light coconut milk", "non dairy milk", "nonfat dried milk", "nonfat dry milk", "nonfat evaporated milk", "nonfat milk", "nonfat powdered milk", "skim milk"], "grade_style": ["organic coconut milk", "organic milk", "unsweetened almond milk", "unsweetened coconut milk", "unsweetened vanilla almond milk"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_milk_cream'})
SET i.canonical_name = 'milk & cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["milk & creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_milk_chocolate'})
SET i.canonical_name = 'milk chocolate',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["milk chocolates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_milk_chocolate_chip'})
SET i.canonical_name = 'milk chocolate chip',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["milk chocolate chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_milk_chocolate_kiss'})
SET i.canonical_name = 'milk chocolate kiss',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_milk_chocolate_piece'})
SET i.canonical_name = 'milk chocolate piece',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["milk chocolate pieces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_millet'})
SET i.canonical_name = 'millet',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["millets"],
    i.variations = '{"other": ["millet"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_millet_flour'})
SET i.canonical_name = 'millet flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["millet flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_miniature_chocolate_chip'})
SET i.canonical_name = 'miniature chocolate chip',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["miniature chocolate chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_miniature_semisweet_chocolate_chip'})
SET i.canonical_name = 'miniature semisweet chocolate chip',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["miniature semisweet chocolate chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mint'})
SET i.canonical_name = 'mint',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["mints"],
    i.variations = '{"other": ["mint"], "cut_or_form": ["dried mint flak"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mint_leaf'})
SET i.canonical_name = 'mint leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["mint leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mint_sauce'})
SET i.canonical_name = 'mint sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["mint sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mint_syrup'})
SET i.canonical_name = 'mint syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["mint syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_minute_rice'})
SET i.canonical_name = 'minute rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["minute rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_minute_white_rice'})
SET i.canonical_name = 'minute white rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["minute white rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mirin'})
SET i.canonical_name = 'mirin',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["mirins"],
    i.variations = '{"other": ["mirin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_miso'})
SET i.canonical_name = 'miso',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["misos"],
    i.variations = '{"other": ["miso"], "grade_style": ["sweet white miso"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_miso_paste'})
SET i.canonical_name = 'miso paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["miso pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_miso_sesame_grilling_sauce'})
SET i.canonical_name = 'miso sesame grilling sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["miso sesame grilling sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mizkan_rice_vinegar'})
SET i.canonical_name = 'mizkan rice vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["mizkan rice vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mojo_marinade'})
SET i.canonical_name = 'mojo marinade',
    i.category = 'condiment',
    i.base = 'marinade',
    i.alt_names = ["mojo marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_molass'})
SET i.canonical_name = 'molass',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["molasses"],
    i.variations = '{"other": ["molass"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_molasses'})
SET i.canonical_name = 'molasses',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["molasseses"],
    i.variations = '{"other": ["unsulphured molasses"], "nutrition": ["light molasses"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_molasses_sugar'})
SET i.canonical_name = 'molasses sugar',
    i.category = 'sweetener',
    i.base = 'molasses',
    i.alt_names = ["molasses sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mole_paste'})
SET i.canonical_name = 'mole paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["mole pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mole_sauce'})
SET i.canonical_name = 'mole sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["mole sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mortadella'})
SET i.canonical_name = 'mortadella',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["mortadellas"],
    i.variations = '{"other": ["mortadella"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_morton_salt'})
SET i.canonical_name = 'morton salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["morton salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mozzarella'})
SET i.canonical_name = 'mozzarella',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["mozzarellas"],
    i.variations = '{"other": ["mozzarella"], "cut_or_form": ["smoked mozzarella"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mozzarella_cheese'})
SET i.canonical_name = 'mozzarella cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["mozzarella cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_muenster_cheese'})
SET i.canonical_name = 'muenster cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["muenster cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_multi_grain_penne_pasta'})
SET i.canonical_name = 'multi-grain penne pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["multi-grain penne pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_multigrain_bread'})
SET i.canonical_name = 'multigrain bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["multigrain breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_multigrain_cereal'})
SET i.canonical_name = 'multigrain cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["multigrain cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mung_bean'})
SET i.canonical_name = 'mung bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["mung beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mung_bean_noodle'})
SET i.canonical_name = 'mung bean noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["mung bean noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mung_bean_sprout'})
SET i.canonical_name = 'mung bean sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["mung bean sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mung_bean_vermicelli'})
SET i.canonical_name = 'mung bean vermicelli',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["mung bean vermicellis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_muscovado_sugar'})
SET i.canonical_name = 'muscovado sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["muscovado sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mushroom'})
SET i.canonical_name = 'mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["mushrooms"],
    i.variations = '{"other": ["baby portobello mushroom", "mushroom", "tree ear mushroom"], "cut_or_form": ["dried black mushroom", "dried mushroom", "dried porcini mushroom", "dried shiitake mushroom", "dried wood ear mushroom", "fresh mushroom", "fresh shiitake mushroom"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mushroom_broth'})
SET i.canonical_name = 'mushroom broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["mushroom broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mushroom_sauce'})
SET i.canonical_name = 'mushroom sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["mushroom sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mushroom_soup'})
SET i.canonical_name = 'mushroom soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["mushroom soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mussel'})
SET i.canonical_name = 'mussel',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["mussels"],
    i.variations = '{"other": ["mussel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mustard'})
SET i.canonical_name = 'mustard',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["mustards"],
    i.variations = '{"other": ["dry mustard", "prepared mustard"], "cut_or_form": ["coarse ground mustard", "ground mustard", "stone ground mustard", "whole grain dijon mustard", "whole grain mustard"], "grade_style": ["sweet mustard"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_mustard_green'})
SET i.canonical_name = 'mustard green',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["mustard greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mustard_oil'})
SET i.canonical_name = 'mustard oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["mustard oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mustard_powder'})
SET i.canonical_name = 'mustard powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["mustard powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mustard_sauce'})
SET i.canonical_name = 'mustard sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["mustard sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_mutton'})
SET i.canonical_name = 'mutton',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["muttons"],
    i.variations = '{"other": ["mutton"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_naan'})
SET i.canonical_name = 'naan',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["naans"],
    i.variations = '{"other": ["naan", "stonefire tandoori garlic naan"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_nacho_cheese_tortilla_chip'})
SET i.canonical_name = 'nacho cheese tortilla chip',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["nacho cheese tortilla chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_nacho_chip'})
SET i.canonical_name = 'nacho chip',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["nacho chips", "nachochip", "nachochips"],
    i.variations = '{"other": ["nacho chip"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_napa_cabbage'})
SET i.canonical_name = 'napa cabbage',
    i.category = 'vegetable',
    i.base = 'cabbage',
    i.alt_names = ["napa cabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_napa_cabbage_leaf'})
SET i.canonical_name = 'napa cabbage leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["napa cabbage leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_nappa_cabbage'})
SET i.canonical_name = 'nappa cabbage',
    i.category = 'vegetable',
    i.base = 'cabbage',
    i.alt_names = ["nappa cabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_natural_peanut_butter'})
SET i.canonical_name = 'natural peanut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["natural peanut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_natural_sugar'})
SET i.canonical_name = 'natural sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["natural sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_natural_yogurt'})
SET i.canonical_name = 'natural yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["natural yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_navel_orange'})
SET i.canonical_name = 'navel orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["navel oranges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_navy_bean'})
SET i.canonical_name = 'navy bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["navy beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_neapolitan_ice_cream'})
SET i.canonical_name = 'neapolitan ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["neapolitan ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_nectarine'})
SET i.canonical_name = 'nectarine',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["nectarines"],
    i.variations = '{"other": ["nectarine"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_neutral_oil'})
SET i.canonical_name = 'neutral oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["neutral oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_nido_milk_powder'})
SET i.canonical_name = 'nido milk powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["nido milk powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_noodle'})
SET i.canonical_name = 'noodle',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["noodles"],
    i.variations = '{"other": ["noodle", "rice stick noodle", "thin rice stick noodle", "wide egg noodle", "wide rice noodle"], "cut_or_form": ["dried rice noodle", "whole wheat lasagna noodle", "whole wheat spaghetti noodle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_nori_flak'})
SET i.canonical_name = 'nori flak',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["nori flaks", "noriflak", "noriflaks"],
    i.variations = '{"other": ["nori flak"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_nut_butter'})
SET i.canonical_name = 'nut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["nut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_nut_oil'})
SET i.canonical_name = 'nut oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["nut oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_nutmeg'})
SET i.canonical_name = 'nutmeg',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["nutmegs"],
    i.variations = '{"other": ["nutmeg"], "cut_or_form": ["ground nutmeg", "simply organic ground nutmeg", "whole nutmeg"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_nutritional_yeast_flak'})
SET i.canonical_name = 'nutritional yeast flak',
    i.category = 'baking',
    i.base = 'yeast',
    i.alt_names = ["nutritional yeast flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oat'})
SET i.canonical_name = 'oat',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["oats"],
    i.variations = '{"other": ["oat"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_oat_bran'})
SET i.canonical_name = 'oat bran',
    i.category = 'grain',
    i.base = 'oat',
    i.alt_names = ["oat brans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oat_flour'})
SET i.canonical_name = 'oat flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["oat flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oat_groat'})
SET i.canonical_name = 'oat groat',
    i.category = 'grain',
    i.base = 'oat',
    i.alt_names = ["oat groats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oat_milk'})
SET i.canonical_name = 'oat milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["oat milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oats'})
SET i.canonical_name = 'oats',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["oatses"],
    i.variations = '{"other": ["flaked oats", "instant oats", "oats"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_oelek'})
SET i.canonical_name = 'oelek',
    i.category = 'sauce',
    i.base = null,
    i.alt_names = ["oeleks"],
    i.variations = '{"other": ["oelek"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_oil'})
SET i.canonical_name = 'oil',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["oils"],
    i.variations = '{"other": ["pumpkin seed oil", "stir fry oil", "toasted sesame oil"], "grade_style": ["organic coconut oil", "pure olive oil", "pure wesson canola oil", "pure wesson vegetable oil", "virgin coconut oil", "virgin olive oil"], "cut_or_form": ["roasted almond oil", "roasted garlic oil"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_oil_cured_olive'})
SET i.canonical_name = 'oil cured olive',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["oil cured olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oil_cured_black_olive'})
SET i.canonical_name = 'oil-cured black olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["oil-cured black olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_okra'})
SET i.canonical_name = 'okra',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["okras"],
    i.variations = '{"other": ["okra"], "cut_or_form": ["whole baby okra", "whole okra"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_old_ginger'})
SET i.canonical_name = 'old ginger',
    i.category = 'seasoning',
    i.base = 'ginger',
    i.alt_names = ["old gingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_old_fashioned_oats'})
SET i.canonical_name = 'old-fashioned oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_olive'})
SET i.canonical_name = 'olive',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["olives"],
    i.variations = '{"other": ["brine-cured olive", "niçoise olive", "olive", "pimento stuffed olive", "pitted kalamata olive", "pitted olive"], "variety": ["brine cured green olive", "brine-cured black olive", "castelvetrano olive", "pimento stuffed green olive", "pitted black olive", "pitted green olive"], "cut_or_form": ["cracked green olive"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_olive_oil'})
SET i.canonical_name = 'olive oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["olive oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_olive_oil_mayonnaise'})
SET i.canonical_name = 'olive oil mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["olive oil mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_olive_oil_spray'})
SET i.canonical_name = 'olive oil spray',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["olive oil spraies"],
    i.variations = null;

// Progress: 1400/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_olive_tapenade'})
SET i.canonical_name = 'olive tapenade',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["olive tapenades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion'})
SET i.canonical_name = 'onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["onions"],
    i.variations = '{"other": ["onion"], "cut_or_form": ["fresh onion"], "grade_style": ["sweet onion"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_onion_flak'})
SET i.canonical_name = 'onion flak',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["onion flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion_gravy'})
SET i.canonical_name = 'onion gravy',
    i.category = 'condiment',
    i.base = 'gravy',
    i.alt_names = ["onion gravies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion_powder'})
SET i.canonical_name = 'onion powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["onion powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion_salt'})
SET i.canonical_name = 'onion salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["onion salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion_slice'})
SET i.canonical_name = 'onion slice',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["onion slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion_soup'})
SET i.canonical_name = 'onion soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["onion soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_onion_top'})
SET i.canonical_name = 'onion top',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["onion tops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange'})
SET i.canonical_name = 'orange',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["oranges"],
    i.variations = '{"cut_or_form": ["fresh orange"], "nutrition": ["diet orange soda"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_orange_bitter'})
SET i.canonical_name = 'orange bitter',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange bitters", "orangebitter", "orangebitters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_blossom_honey'})
SET i.canonical_name = 'orange blossom honey',
    i.category = 'herb',
    i.base = 'blossom',
    i.alt_names = ["orange blossom honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_flower_water'})
SET i.canonical_name = 'orange flower water',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["orange flower waters", "orangeflowerwater", "orangeflowerwaters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_glaze'})
SET i.canonical_name = 'orange glaze',
    i.category = 'condiment',
    i.base = 'glaze',
    i.alt_names = ["orange glazes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_juice'})
SET i.canonical_name = 'orange juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["orange juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_juice_concentrate'})
SET i.canonical_name = 'orange juice concentrate',
    i.category = 'condiment',
    i.base = 'concentrate',
    i.alt_names = ["orange juice concentrates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_lentil'})
SET i.canonical_name = 'orange lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["orange lentils", "orangelentil", "orangelentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_liqueur'})
SET i.canonical_name = 'orange liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["orange liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_marmalade'})
SET i.canonical_name = 'orange marmalade',
    i.category = 'condiment',
    i.base = 'marmalade',
    i.alt_names = ["orange marmalades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_peel'})
SET i.canonical_name = 'orange peel',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange peels", "orangepeel", "orangepeels"],
    i.variations = '{"cut_or_form": ["dried orange peel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_orange_pekoe_tea'})
SET i.canonical_name = 'orange pekoe tea',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["orange pekoe teas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_rind'})
SET i.canonical_name = 'orange rind',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange rinds", "orangerind", "orangerinds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_roughy'})
SET i.canonical_name = 'orange roughy',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange roughies", "orangeroughies", "orangeroughy"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_roughy_fillet'})
SET i.canonical_name = 'orange roughy fillet',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["orange roughy fillets", "orangeroughyfillet", "orangeroughyfillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_segment'})
SET i.canonical_name = 'orange segment',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange segments", "orangesegment", "orangesegments"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_slice'})
SET i.canonical_name = 'orange slice',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange slices", "orangeslice", "orangeslices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_soda'})
SET i.canonical_name = 'orange soda',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange sodas", "orangesoda", "orangesodas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orange_zest'})
SET i.canonical_name = 'orange zest',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["orange zests", "orangezest", "orangezests"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oregano'})
SET i.canonical_name = 'oregano',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["oreganos"],
    i.variations = '{"other": ["oregano"], "cut_or_form": ["dried oregano"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_orgeat_syrup'})
SET i.canonical_name = 'orgeat syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["orgeat syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oriental_radish'})
SET i.canonical_name = 'oriental radish',
    i.category = 'vegetable',
    i.base = 'radish',
    i.alt_names = ["oriental radishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ornamental_kale'})
SET i.canonical_name = 'ornamental kale',
    i.category = 'vegetable',
    i.base = 'kale',
    i.alt_names = ["ornamental kales"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_orzo'})
SET i.canonical_name = 'orzo',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["orzos"],
    i.variations = '{"other": ["orzo"], "cut_or_form": ["whole wheat orzo"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_orzo_pasta'})
SET i.canonical_name = 'orzo pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["orzo pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oven_ready_lasagna_noodle'})
SET i.canonical_name = 'oven-ready lasagna noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["oven-ready lasagna noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oxtail'})
SET i.canonical_name = 'oxtail',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["oxtails"],
    i.variations = '{"other": ["oxtail"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_oyster'})
SET i.canonical_name = 'oyster',
    i.category = 'sauce',
    i.base = null,
    i.alt_names = ["oysters"],
    i.variations = '{"other": ["oyster", "shucked oyster"], "cut_or_form": ["dried oyster"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_oyster_liquor'})
SET i.canonical_name = 'oyster liquor',
    i.category = 'sauce',
    i.base = 'oyster',
    i.alt_names = ["oyster liquors"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oyster_mushroom'})
SET i.canonical_name = 'oyster mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["oyster mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_oyster_sauce'})
SET i.canonical_name = 'oyster sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["oyster sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_padron_pepper'})
SET i.canonical_name = 'padron pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["padron peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_paella_rice'})
SET i.canonical_name = 'paella rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["paella rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_palm_oil'})
SET i.canonical_name = 'palm oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["palm oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_palm_sugar'})
SET i.canonical_name = 'palm sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["palm sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_palm_vinegar'})
SET i.canonical_name = 'palm vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["palm vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_panang_curry_paste'})
SET i.canonical_name = 'panang curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["panang curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pancetta'})
SET i.canonical_name = 'pancetta',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["pancettas"],
    i.variations = '{"other": ["pancetta"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pandanus_leaf'})
SET i.canonical_name = 'pandanus leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["pandanus leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_paneer_cheese'})
SET i.canonical_name = 'paneer cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["paneer cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_panko_breadcrumb'})
SET i.canonical_name = 'panko breadcrumb',
    i.category = 'grain',
    i.base = 'breadcrumb',
    i.alt_names = ["panko breadcrumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_papaya'})
SET i.canonical_name = 'papaya',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["papayas"],
    i.variations = '{"other": ["papaya"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pappardelle'})
SET i.canonical_name = 'pappardelle',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["pappardelles"],
    i.variations = '{"other": ["pappardelle"], "cut_or_form": ["dried pappardelle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pappardelle_pasta'})
SET i.canonical_name = 'pappardelle pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["pappardelle pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_paprika'})
SET i.canonical_name = 'paprika',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["paprikas"],
    i.variations = '{"other": ["paprika"], "grade_style": ["sweet paprika"], "cut_or_form": ["ground paprika", "hot smoked paprika", "smoked paprika"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_paprika_paste'})
SET i.canonical_name = 'paprika paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["paprika pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_parboiled_rice'})
SET i.canonical_name = 'parboiled rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["parboiled rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_parmesan_cheese'})
SET i.canonical_name = 'parmesan cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["parmesan cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_parsley'})
SET i.canonical_name = 'parsley',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["parsleies"],
    i.variations = '{"other": ["parsley"], "cut_or_form": ["dried parsley"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_parsley_flak'})
SET i.canonical_name = 'parsley flak',
    i.category = 'herb',
    i.base = 'parsley',
    i.alt_names = ["parsley flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_parsley_leaf'})
SET i.canonical_name = 'parsley leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["parsley leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_parsnip'})
SET i.canonical_name = 'parsnip',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["parsnips"],
    i.variations = '{"other": ["parsnip"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pasilla_pepper'})
SET i.canonical_name = 'pasilla pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["pasilla peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_passion_fruit'})
SET i.canonical_name = 'passion fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["passion fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_passion_fruit_juice'})
SET i.canonical_name = 'passion fruit juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["passion fruit juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_passover_cake_meal'})
SET i.canonical_name = 'passover cake meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["passover cake meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_passover_wine'})
SET i.canonical_name = 'passover wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["passover wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta'})
SET i.canonical_name = 'pasta',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["pastas"],
    i.variations = '{"other": ["bow-tie pasta", "dry pasta", "pasta", "smooth pasta"], "cut_or_form": ["dried pasta", "fresh pasta", "whole grain pasta", "whole wheat pasta", "whole wheat penne pasta", "whole wheat rotini pasta", "whole wheat spiral pasta"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_sauce'})
SET i.canonical_name = 'pasta sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["pasta sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_shap'})
SET i.canonical_name = 'pasta shap',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["pasta shaps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_sheet'})
SET i.canonical_name = 'pasta sheet',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["pasta sheets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_shell'})
SET i.canonical_name = 'pasta shell',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["pasta shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_spiral'})
SET i.canonical_name = 'pasta spiral',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["pasta spirals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_wagon_wheel'})
SET i.canonical_name = 'pasta wagon wheel',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["pasta wagon wheels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pasta_water'})
SET i.canonical_name = 'pasta water',
    i.category = 'beverage',
    i.base = 'water',
    i.alt_names = ["pasta waters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_paste'})
SET i.canonical_name = 'paste',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["pastes"],
    i.variations = '{"cut_or_form": ["roasted chili paste"], "grade_style": ["sweet bean paste", "sweet red bean paste", "sweet white miso paste"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pastry'})
SET i.canonical_name = 'pastry',
    i.category = 'baking',
    i.base = null,
    i.alt_names = ["pastries"],
    i.variations = '{"other": ["pastry"], "cut_or_form": ["frozen pastry puff sheet"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pastry_cream'})
SET i.canonical_name = 'pastry cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["pastry creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pastry_dough'})
SET i.canonical_name = 'pastry dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["pastry doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pastry_flour'})
SET i.canonical_name = 'pastry flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["pastry flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pastry_shell'})
SET i.canonical_name = 'pastry shell',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["pastry shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pastry_tart_shell'})
SET i.canonical_name = 'pastry tart shell',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["pastry tart shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pea'})
SET i.canonical_name = 'pea',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["peas"],
    i.variations = '{"other": ["pea"], "cut_or_form": ["dried split pea", "fresh green pea", "fresh pea", "frozen garden pea", "frozen pea", "frozen sweet pea"], "grade_style": ["sweet pea"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pea_eggplant'})
SET i.canonical_name = 'pea eggplant',
    i.category = 'vegetable',
    i.base = 'eggplant',
    i.alt_names = ["pea eggplants"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pea_pod'})
SET i.canonical_name = 'pea pod',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["pea pods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pea_shoot'})
SET i.canonical_name = 'pea shoot',
    i.category = 'vegetable',
    i.base = 'shoot',
    i.alt_names = ["pea shoots"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach'})
SET i.canonical_name = 'peach',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["peaches"],
    i.variations = '{"other": ["peach", "peach purée"], "cut_or_form": ["dried peach", "frozen peach"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_peach_jam'})
SET i.canonical_name = 'peach jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["peach jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_juice'})
SET i.canonical_name = 'peach juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["peach juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_nectar'})
SET i.canonical_name = 'peach nectar',
    i.category = 'fruit',
    i.base = 'peach',
    i.alt_names = ["peach nectars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_preserve'})
SET i.canonical_name = 'peach preserve',
    i.category = 'fruit',
    i.base = 'peach',
    i.alt_names = ["peach preserves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_salsa'})
SET i.canonical_name = 'peach salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["peach salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_schnapp'})
SET i.canonical_name = 'peach schnapp',
    i.category = 'fruit',
    i.base = 'peach',
    i.alt_names = ["peach schnapps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_slice'})
SET i.canonical_name = 'peach slice',
    i.category = 'fruit',
    i.base = 'peach',
    i.alt_names = ["peach slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_sorbet'})
SET i.canonical_name = 'peach sorbet',
    i.category = 'fruit',
    i.base = 'peach',
    i.alt_names = ["peach sorbets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_vodka'})
SET i.canonical_name = 'peach vodka',
    i.category = 'beverage',
    i.base = 'vodka',
    i.alt_names = ["peach vodkas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peach_yogurt'})
SET i.canonical_name = 'peach yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["peach yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peanut'})
SET i.canonical_name = 'peanut',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["peanuts"],
    i.variations = '{"other": ["peanut"], "cut_or_form": ["ground peanut", "honey roasted peanut"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_peanut_brittle'})
SET i.canonical_name = 'peanut brittle',
    i.category = 'nut_or_seed',
    i.base = 'peanut',
    i.alt_names = ["peanut brittles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peanut_butter'})
SET i.canonical_name = 'peanut butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["peanut butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peanut_butter_chip'})
SET i.canonical_name = 'peanut butter chip',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["peanut butter chips"],
    i.variations = null;

// Progress: 1500/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_peanut_oil'})
SET i.canonical_name = 'peanut oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["peanut oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peanut_powder'})
SET i.canonical_name = 'peanut powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["peanut powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peanut_sauce'})
SET i.canonical_name = 'peanut sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["peanut sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pear'})
SET i.canonical_name = 'pear',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["pears"],
    i.variations = '{"other": ["pear"], "cut_or_form": ["dried pear"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pear_juice'})
SET i.canonical_name = 'pear juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["pear juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pear_tomato'})
SET i.canonical_name = 'pear tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["pear tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pearl_barley'})
SET i.canonical_name = 'pearl barley',
    i.category = 'grain',
    i.base = 'barley',
    i.alt_names = ["pearl barleies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pearl_couscous'})
SET i.canonical_name = 'pearl couscous',
    i.category = 'grain',
    i.base = 'couscous',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pearl_onion'})
SET i.canonical_name = 'pearl onion',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["pearl onions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pearl_rice'})
SET i.canonical_name = 'pearl rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["pearl rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pearl_tapioca'})
SET i.canonical_name = 'pearl tapioca',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["pearl tapiocas", "pearltapioca", "pearltapiocas"],
    i.variations = '{"other": ["pearl tapioca"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_peasant_bread'})
SET i.canonical_name = 'peasant bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["peasant breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pecan'})
SET i.canonical_name = 'pecan',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["pecans"],
    i.variations = '{"other": ["pecan"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pecan_pie'})
SET i.canonical_name = 'pecan pie',
    i.category = 'nut_or_seed',
    i.base = 'pecan',
    i.alt_names = ["pecan pies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_penne'})
SET i.canonical_name = 'penne',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["pennes"],
    i.variations = '{"other": ["penne"], "cut_or_form": ["whole wheat penne"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_penne_pasta'})
SET i.canonical_name = 'penne pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["penne pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_penne_rigate'})
SET i.canonical_name = 'penne rigate',
    i.category = 'grain',
    i.base = 'penne',
    i.alt_names = ["penne rigates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepita'})
SET i.canonical_name = 'pepita',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["pepitas"],
    i.variations = '{"other": ["pepita"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pepper'})
SET i.canonical_name = 'pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["peppers"],
    i.variations = '{"other": ["dr pepper", "dr. pepper", "pepper"], "variety": ["fresno pepper", "poblano pepper", "serrano pepper"], "grade_style": ["sweet pepper"], "cut_or_form": ["ancho chili ground pepper", "canned jalapeno pepper", "dried chipotle pepper", "fresh poblano pepper", "freshly ground pepper", "ground cayenne pepper", "ground pepper", "ground red pepper", "ground roasted sichuan pepper", "ground sichuan pepper", "roasted bell pepper", "roasted red pepper"], "nutrition": ["diet dr. pepper"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pepper_cheese'})
SET i.canonical_name = 'pepper cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["pepper cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepper_flak'})
SET i.canonical_name = 'pepper flak',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["pepper flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepper_jack'})
SET i.canonical_name = 'pepper jack',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["pepper jacks", "pepperjack", "pepperjacks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepper_leaf'})
SET i.canonical_name = 'pepper leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["pepper leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepper_sauce'})
SET i.canonical_name = 'pepper sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["pepper sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepper_vodka'})
SET i.canonical_name = 'pepper vodka',
    i.category = 'beverage',
    i.base = 'vodka',
    i.alt_names = ["pepper vodkas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_peppercorn'})
SET i.canonical_name = 'peppercorn',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["peppercorns"],
    i.variations = '{"other": ["peppercorn"], "cut_or_form": ["cracked peppercorn", "whole peppercorn"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pepperidge_farm_puff_pastry'})
SET i.canonical_name = 'pepperidge farm puff pastry',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["pepperidge farm puff pastries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pepperoncini'})
SET i.canonical_name = 'pepperoncini',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["pepperoncinis"],
    i.variations = '{"other": ["pepperoncini"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pepperoni'})
SET i.canonical_name = 'pepperoni',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["pepperonis"],
    i.variations = '{"other": ["pepperoni"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pernod_liqueur'})
SET i.canonical_name = 'pernod liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["pernod liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pesto'})
SET i.canonical_name = 'pesto',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["pestos"],
    i.variations = '{"other": ["prepar pesto", "sundried tomato pesto"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pesto_sauce'})
SET i.canonical_name = 'pesto sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["pesto sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_petite_pea'})
SET i.canonical_name = 'petite pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["petite peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pheasant'})
SET i.canonical_name = 'pheasant',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["pheasants"],
    i.variations = '{"other": ["pheasant"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_phyllo_dough'})
SET i.canonical_name = 'phyllo dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["phyllo doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_phyllo_pastry'})
SET i.canonical_name = 'phyllo pastry',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["phyllo pastries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_picante_sauce'})
SET i.canonical_name = 'picante sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["picante sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_picholine'})
SET i.canonical_name = 'picholine',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["picholines"],
    i.variations = '{"other": ["picholine"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_picholine_olive'})
SET i.canonical_name = 'picholine olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["picholine olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickapeppa_sauce'})
SET i.canonical_name = 'pickapeppa sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["pickapeppa sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickle'})
SET i.canonical_name = 'pickle',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["pickles"],
    i.variations = '{"other": ["pickle"], "grade_style": ["sweet pickle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pickle_juice'})
SET i.canonical_name = 'pickle juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["pickle juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickle_relish'})
SET i.canonical_name = 'pickle relish',
    i.category = 'condiment',
    i.base = 'relish',
    i.alt_names = ["pickle relishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickle_spear'})
SET i.canonical_name = 'pickle spear',
    i.category = 'condiment',
    i.base = 'pickle',
    i.alt_names = ["pickle spears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickle_wedge'})
SET i.canonical_name = 'pickle wedge',
    i.category = 'condiment',
    i.base = 'pickle',
    i.alt_names = ["pickle wedges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickling_cucumber'})
SET i.canonical_name = 'pickling cucumber',
    i.category = 'vegetable',
    i.base = 'cucumber',
    i.alt_names = ["pickling cucumbers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickling_liquid'})
SET i.canonical_name = 'pickling liquid',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["pickling liquids", "picklingliquid", "picklingliquids"],
    i.variations = '{"other": ["pickling liquid"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pickling_salt'})
SET i.canonical_name = 'pickling salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["pickling salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pickling_spice'})
SET i.canonical_name = 'pickling spice',
    i.category = 'seasoning',
    i.base = 'spice',
    i.alt_names = ["pickling spices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pie_crust'})
SET i.canonical_name = 'pie crust',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["pie crusts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pie_dough'})
SET i.canonical_name = 'pie dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["pie doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pie_pastry'})
SET i.canonical_name = 'pie pastry',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["pie pastries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pie_shell'})
SET i.canonical_name = 'pie shell',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["pie shells", "pieshell", "pieshells"],
    i.variations = '{"other": ["pie shell"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pigeon_pea'})
SET i.canonical_name = 'pigeon pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["pigeon peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pillsbury_pie_crust'})
SET i.canonical_name = 'pillsbury pie crust',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["pillsbury pie crusts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pine_nut'})
SET i.canonical_name = 'pine nut',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["pine nuts", "pinenut", "pinenuts"],
    i.variations = '{"other": ["pine nut"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple'})
SET i.canonical_name = 'pineapple',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["pineapples"],
    i.variations = '{"other": ["golden pineapple", "pineapple"], "cut_or_form": ["dried pineapple", "fresh pineapple"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_chunk'})
SET i.canonical_name = 'pineapple chunk',
    i.category = 'fruit',
    i.base = 'pineapple',
    i.alt_names = ["pineapple chunks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_juice'})
SET i.canonical_name = 'pineapple juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["pineapple juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_juice_concentrate'})
SET i.canonical_name = 'pineapple juice concentrate',
    i.category = 'condiment',
    i.base = 'concentrate',
    i.alt_names = ["pineapple juice concentrates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_preserve'})
SET i.canonical_name = 'pineapple preserve',
    i.category = 'fruit',
    i.base = 'pineapple',
    i.alt_names = ["pineapple preserves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_salsa'})
SET i.canonical_name = 'pineapple salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["pineapple salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_slice'})
SET i.canonical_name = 'pineapple slice',
    i.category = 'fruit',
    i.base = 'pineapple',
    i.alt_names = ["pineapple slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pineapple_syrup'})
SET i.canonical_name = 'pineapple syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["pineapple syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_bean'})
SET i.canonical_name = 'pink bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["pink beans", "pinkbean", "pinkbeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_grapefruit'})
SET i.canonical_name = 'pink grapefruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["pink grapefruits", "pinkgrapefruit", "pinkgrapefruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_grapefruit_juice'})
SET i.canonical_name = 'pink grapefruit juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["pink grapefruit juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_lady_apple'})
SET i.canonical_name = 'pink lady apple',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["pink lady apples", "pinkladyapple", "pinkladyapples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_lentil'})
SET i.canonical_name = 'pink lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["pink lentils", "pinklentil", "pinklentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_peppercorn'})
SET i.canonical_name = 'pink peppercorn',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["pink peppercorns", "pinkpeppercorn", "pinkpeppercorns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_salmon'})
SET i.canonical_name = 'pink salmon',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["pink salmons", "pinksalmon", "pinksalmons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pink_salt'})
SET i.canonical_name = 'pink salt',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["pink salts", "pinksalt", "pinksalts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pinto_bean'})
SET i.canonical_name = 'pinto bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["pinto beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pippin_apple'})
SET i.canonical_name = 'pippin apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["pippin apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_piquillo_pepper'})
SET i.canonical_name = 'piquillo pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["piquillo peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_piri_piri_sauce'})
SET i.canonical_name = 'piri-piri sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["piri-piri sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pistachio'})
SET i.canonical_name = 'pistachio',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["pistachios"],
    i.variations = '{"other": ["pistachio", "raw pistachio"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pita'})
SET i.canonical_name = 'pita',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["pitas"],
    i.variations = '{"other": ["pita", "pita bread round"], "cut_or_form": ["whole wheat pita"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pita_bread'})
SET i.canonical_name = 'pita bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["pita breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pita_chip'})
SET i.canonical_name = 'pita chip',
    i.category = 'grain',
    i.base = 'pita',
    i.alt_names = ["pita chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pitted_date'})
SET i.canonical_name = 'pitted date',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["pitted dates", "pitteddate", "pitteddates"],
    i.variations = '{"other": ["pitted date"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pizza_sauce'})
SET i.canonical_name = 'pizza sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["pizza sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_plum'})
SET i.canonical_name = 'plum',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["plums"],
    i.variations = '{"other": ["plum"], "cut_or_form": ["dried plum"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_plum_jam'})
SET i.canonical_name = 'plum jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["plum jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_plum_sauce'})
SET i.canonical_name = 'plum sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["plum sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_plum_tomato'})
SET i.canonical_name = 'plum tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["plum tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_plum_wine'})
SET i.canonical_name = 'plum wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["plum wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pocket_bread'})
SET i.canonical_name = 'pocket bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["pocket breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pointed_pepper'})
SET i.canonical_name = 'pointed pepper',
    i.category = 'vegetable',
    i.base = 'pepper',
    i.alt_names = ["pointed peppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_polenta'})
SET i.canonical_name = 'polenta',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["polentas"],
    i.variations = '{"other": ["polenta", "polenta prepar"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_polenta_corn_meal'})
SET i.canonical_name = 'polenta corn meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["polenta corn meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pomegranate_juice'})
SET i.canonical_name = 'pomegranate juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["pomegranate juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pomegranate_molasses'})
SET i.canonical_name = 'pomegranate molasses',
    i.category = 'sweetener',
    i.base = 'molasses',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pomegranate_syrup'})
SET i.canonical_name = 'pomegranate syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["pomegranate syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pomelo'})
SET i.canonical_name = 'pomelo',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["pomelos"],
    i.variations = '{"other": ["pomelo"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_popcorn_chicken'})
SET i.canonical_name = 'popcorn chicken',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["popcorn chickens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_porcini_powder'})
SET i.canonical_name = 'porcini powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["porcini powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork'})
SET i.canonical_name = 'pork',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["porks"],
    i.variations = '{"other": ["pork"], "cut_or_form": ["boneless country pork rib", "cubed pork", "ground pork", "lean ground pork", "pork baby back rib", "smoked pork", "smoked pork neck bon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_pork_back_rib'})
SET i.canonical_name = 'pork back rib',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork back ribs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_blade_steak'})
SET i.canonical_name = 'pork blade steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["pork blade steaks"],
    i.variations = null;

// Progress: 1600/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_pork_blood'})
SET i.canonical_name = 'pork blood',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork bloods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_bon'})
SET i.canonical_name = 'pork bon',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_butt'})
SET i.canonical_name = 'pork butt',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork butts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_butt_roast'})
SET i.canonical_name = 'pork butt roast',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork butt roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_cheek'})
SET i.canonical_name = 'pork cheek',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork cheeks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_chop'})
SET i.canonical_name = 'pork chop',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_cub'})
SET i.canonical_name = 'pork cub',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork cubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_cutlet'})
SET i.canonical_name = 'pork cutlet',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork cutlets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_fillet'})
SET i.canonical_name = 'pork fillet',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_heart'})
SET i.canonical_name = 'pork heart',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_hock'})
SET i.canonical_name = 'pork hock',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork hocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_lard'})
SET i.canonical_name = 'pork lard',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork lards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_leg'})
SET i.canonical_name = 'pork leg',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork legs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_liver'})
SET i.canonical_name = 'pork liver',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork livers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_loin'})
SET i.canonical_name = 'pork loin',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork loins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_loin_chop'})
SET i.canonical_name = 'pork loin chop',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork loin chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_loin_rib_chop'})
SET i.canonical_name = 'pork loin rib chop',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork loin rib chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_meat'})
SET i.canonical_name = 'pork meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["pork meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_neck'})
SET i.canonical_name = 'pork neck',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork necks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_picnic_roast'})
SET i.canonical_name = 'pork picnic roast',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork picnic roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_rib'})
SET i.canonical_name = 'pork rib',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork ribs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_rib_chop'})
SET i.canonical_name = 'pork rib chop',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork rib chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_rind'})
SET i.canonical_name = 'pork rind',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork rinds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_roast'})
SET i.canonical_name = 'pork roast',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_roll'})
SET i.canonical_name = 'pork roll',
    i.category = 'grain',
    i.base = 'roll',
    i.alt_names = ["pork rolls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_rub'})
SET i.canonical_name = 'pork rub',
    i.category = 'other',
    i.base = 'rub',
    i.alt_names = ["pork rubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_sausage'})
SET i.canonical_name = 'pork sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["pork sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_sausage_link'})
SET i.canonical_name = 'pork sausage link',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork sausage links"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_shank'})
SET i.canonical_name = 'pork shank',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork shanks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_shoulder'})
SET i.canonical_name = 'pork shoulder',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork shoulders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_shoulder_boston_butt'})
SET i.canonical_name = 'pork shoulder boston butt',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork shoulder boston butts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_shoulder_butt'})
SET i.canonical_name = 'pork shoulder butt',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork shoulder butts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_shoulder_roast'})
SET i.canonical_name = 'pork shoulder roast',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork shoulder roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_sirloin'})
SET i.canonical_name = 'pork sirloin',
    i.category = 'meat',
    i.base = 'sirloin',
    i.alt_names = ["pork sirloins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_sirloin_chop'})
SET i.canonical_name = 'pork sirloin chop',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork sirloin chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_sirloin_roast'})
SET i.canonical_name = 'pork sirloin roast',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork sirloin roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_spare_rib'})
SET i.canonical_name = 'pork spare rib',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork spare ribs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_sparerib'})
SET i.canonical_name = 'pork sparerib',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork spareribs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_steak'})
SET i.canonical_name = 'pork steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["pork steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_stew_meat'})
SET i.canonical_name = 'pork stew meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["pork stew meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_stock'})
SET i.canonical_name = 'pork stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["pork stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_strip'})
SET i.canonical_name = 'pork strip',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork strips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_tail'})
SET i.canonical_name = 'pork tail',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork tails"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_tenderloin'})
SET i.canonical_name = 'pork tenderloin',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork tenderloins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_tenderloin_medallion'})
SET i.canonical_name = 'pork tenderloin medallion',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork tenderloin medallions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_tongue'})
SET i.canonical_name = 'pork tongue',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork tongues"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pork_top_loin_chop'})
SET i.canonical_name = 'pork top loin chop',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["pork top loin chops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_porridge_oats'})
SET i.canonical_name = 'porridge oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_port_wine'})
SET i.canonical_name = 'port wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["port wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pot_pie'})
SET i.canonical_name = 'pot pie',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["pot pies", "potpie", "potpies"],
    i.variations = '{"other": ["pot pie"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_potato'})
SET i.canonical_name = 'potato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["potatoes", "potatos"],
    i.variations = '{"other": ["instant potato flak", "potato", "potato stick"], "grade_style": ["sweet potato vermicelli"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_potato_bread'})
SET i.canonical_name = 'potato bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["potato breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_chip'})
SET i.canonical_name = 'potato chip',
    i.category = 'vegetable',
    i.base = 'potato',
    i.alt_names = ["potato chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_flak'})
SET i.canonical_name = 'potato flak',
    i.category = 'vegetable',
    i.base = 'potato',
    i.alt_names = ["potato flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_flour'})
SET i.canonical_name = 'potato flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["potato flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_gnocchi'})
SET i.canonical_name = 'potato gnocchi',
    i.category = 'grain',
    i.base = 'gnocchi',
    i.alt_names = ["potato gnocchis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_nugget'})
SET i.canonical_name = 'potato nugget',
    i.category = 'vegetable',
    i.base = 'potato',
    i.alt_names = ["potato nuggets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_puree'})
SET i.canonical_name = 'potato puree',
    i.category = 'condiment',
    i.base = 'puree',
    i.alt_names = ["potato purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_roll'})
SET i.canonical_name = 'potato roll',
    i.category = 'grain',
    i.base = 'roll',
    i.alt_names = ["potato rolls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_slider_bun'})
SET i.canonical_name = 'potato slider bun',
    i.category = 'vegetable',
    i.base = 'potato',
    i.alt_names = ["potato slider buns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_soup'})
SET i.canonical_name = 'potato soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["potato soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_starch'})
SET i.canonical_name = 'potato starch',
    i.category = 'grain',
    i.base = 'starch',
    i.alt_names = ["potato starches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_potato_starch_flour'})
SET i.canonical_name = 'potato starch flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["potato starch flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pound_cake'})
SET i.canonical_name = 'pound cake',
    i.category = 'grain',
    i.base = 'cake',
    i.alt_names = ["pound cakes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_powder'})
SET i.canonical_name = 'powder',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["powders"],
    i.variations = '{"other": ["colman\'s mustard powder", "dry milk powder", "file powder", "five-spice powder", "gumbo file powder", "instant espresso powder", "instant tea powder", "knox gelatin powder", "malted milk powder", "spice islands chili powder"], "nutrition": ["nonfat dry milk powder", "nonfat milk powder", "salt free chili powder"], "cut_or_form": ["roasted rice powder"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_powdered_gelatin'})
SET i.canonical_name = 'powdered gelatin',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["powdered gelatins", "powderedgelatin", "powderedgelatins"],
    i.variations = '{"other": ["powdered gelatin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_praline_liqueur'})
SET i.canonical_name = 'praline liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["praline liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_praline_paste'})
SET i.canonical_name = 'praline paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["praline pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_praline_syrup'})
SET i.canonical_name = 'praline syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["praline syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_prawn'})
SET i.canonical_name = 'prawn',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["prawns"],
    i.variations = '{"other": ["prawn", "raw prawn", "raw tiger prawn"], "cut_or_form": ["dried prawn"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_preserved_black_winter_truffle'})
SET i.canonical_name = 'preserved black winter truffle',
    i.category = 'plant_protein',
    i.base = 'black',
    i.alt_names = ["preserved black winter truffles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_preserved_lemon'})
SET i.canonical_name = 'preserved lemon',
    i.category = 'fruit',
    i.base = 'lemon',
    i.alt_names = ["preserved lemons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pretzel'})
SET i.canonical_name = 'pretzel',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["pretzels"],
    i.variations = '{"other": ["pretzel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_processed_cheese'})
SET i.canonical_name = 'processed cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["processed cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_prosciutto'})
SET i.canonical_name = 'prosciutto',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["prosciuttos"],
    i.variations = '{"other": ["prosciutto"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_protein_powder'})
SET i.canonical_name = 'protein powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["protein powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_provolone_cheese'})
SET i.canonical_name = 'provolone cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["provolone cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_prune_juice'})
SET i.canonical_name = 'prune juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["prune juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pudding_powder'})
SET i.canonical_name = 'pudding powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["pudding powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_puff_paste'})
SET i.canonical_name = 'puff paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["puff pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_puff_pastry'})
SET i.canonical_name = 'puff pastry',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["puff pastries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_puff_pastry_cup'})
SET i.canonical_name = 'puff pastry cup',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["puff pastry cups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_puff_pastry_sheet'})
SET i.canonical_name = 'puff pastry sheet',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["puff pastry sheets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_puffed_rice'})
SET i.canonical_name = 'puffed rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["puffed rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pumpernickel_bread'})
SET i.canonical_name = 'pumpernickel bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["pumpernickel breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_pumpkin'})
SET i.canonical_name = 'pumpkin',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["pumpkins"],
    i.variations = '{"other": ["cubed pumpkin", "jamaican pumpkin", "pie pumpkin", "pumpkin purée", "pumpkin seed mole", "solid pack pumpkin", "sugar pumpkin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_puree'})
SET i.canonical_name = 'puree',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_purple_onion'})
SET i.canonical_name = 'purple onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["purple onions", "purpleonion", "purpleonions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_puy_lentil'})
SET i.canonical_name = 'puy lentil',
    i.category = 'plant_protein',
    i.base = 'lentil',
    i.alt_names = ["puy lentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_quahog_clam'})
SET i.canonical_name = 'quahog clam',
    i.category = 'seafood',
    i.base = 'clam',
    i.alt_names = ["quahog clams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_quail'})
SET i.canonical_name = 'quail',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["quails"],
    i.variations = '{"other": ["quail"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_quail_egg'})
SET i.canonical_name = 'quail egg',
    i.category = 'baking',
    i.base = 'egg',
    i.alt_names = ["quail eggs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_quick_oats'})
SET i.canonical_name = 'quick oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_quick_rolled_oats'})
SET i.canonical_name = 'quick rolled oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_quince_paste'})
SET i.canonical_name = 'quince paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["quince pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_quinoa'})
SET i.canonical_name = 'quinoa',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["quinoas"],
    i.variations = '{"other": ["quinoa"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_quinoa_flour'})
SET i.canonical_name = 'quinoa flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["quinoa flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rabbit'})
SET i.canonical_name = 'rabbit',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["rabbits"],
    i.variations = '{"other": ["rabbit"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_radicchio'})
SET i.canonical_name = 'radicchio',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["radicchios"],
    i.variations = '{"other": ["radicchio"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_radicchio_leaf'})
SET i.canonical_name = 'radicchio leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["radicchio leafs"],
    i.variations = null;

// Progress: 1700/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_radish'})
SET i.canonical_name = 'radish',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["radishes"],
    i.variations = '{"other": ["radish"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_radish_slice'})
SET i.canonical_name = 'radish slice',
    i.category = 'vegetable',
    i.base = 'radish',
    i.alt_names = ["radish slices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_radish_sprout'})
SET i.canonical_name = 'radish sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["radish sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ragu_classic_alfredo_sauce'})
SET i.canonical_name = 'ragu classic alfredo sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["ragu classic alfredo sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ragu_sauce'})
SET i.canonical_name = 'ragu sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["ragu sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rainbow_trout'})
SET i.canonical_name = 'rainbow trout',
    i.category = 'seafood',
    i.base = 'trout',
    i.alt_names = ["rainbow trouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raisin'})
SET i.canonical_name = 'raisin',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["raisins"],
    i.variations = '{"other": ["golden raisin", "raisin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_raisin_bread'})
SET i.canonical_name = 'raisin bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["raisin breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ramen_noodle_soup'})
SET i.canonical_name = 'ramen noodle soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["ramen noodle soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ramp'})
SET i.canonical_name = 'ramp',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["ramps"],
    i.variations = '{"other": ["ramp"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rapeseed_oil'})
SET i.canonical_name = 'rapeseed oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["rapeseed oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rasher'})
SET i.canonical_name = 'rasher',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["rashers"],
    i.variations = '{"other": ["rasher"], "cut_or_form": ["smoked rasher"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry'})
SET i.canonical_name = 'raspberry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["raspberries"],
    i.variations = '{"other": ["raspberry"], "cut_or_form": ["dried raspberry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_jam'})
SET i.canonical_name = 'raspberry jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["raspberry jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_juice'})
SET i.canonical_name = 'raspberry juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["raspberry juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_lambic'})
SET i.canonical_name = 'raspberry lambic',
    i.category = 'fruit',
    i.base = 'raspberry',
    i.alt_names = ["raspberry lambics"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_liqueur'})
SET i.canonical_name = 'raspberry liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["raspberry liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_preserve'})
SET i.canonical_name = 'raspberry preserve',
    i.category = 'fruit',
    i.base = 'raspberry',
    i.alt_names = ["raspberry preserves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_puree'})
SET i.canonical_name = 'raspberry puree',
    i.category = 'condiment',
    i.base = 'puree',
    i.alt_names = ["raspberry purees"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_sauce'})
SET i.canonical_name = 'raspberry sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["raspberry sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_sherbet'})
SET i.canonical_name = 'raspberry sherbet',
    i.category = 'fruit',
    i.base = 'raspberry',
    i.alt_names = ["raspberry sherbets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_raspberry_vinegar'})
SET i.canonical_name = 'raspberry vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["raspberry vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ravioli'})
SET i.canonical_name = 'ravioli',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["raviolis"],
    i.variations = '{"product": ["ravioli", "refrigerated four cheese ravioli", "vegetable-filled ravioli"], "cut_or_form": ["frozen cheese ravioli"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_razor_clam'})
SET i.canonical_name = 'razor clam',
    i.category = 'seafood',
    i.base = 'clam',
    i.alt_names = ["razor clams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ready_made_pie_crust'})
SET i.canonical_name = 'ready-made pie crust',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["ready-made pie crusts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red'})
SET i.canonical_name = 'red',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["reds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_anjou_pear'})
SET i.canonical_name = 'red anjou pear',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red anjou pears", "redanjoupear", "redanjoupears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_apple'})
SET i.canonical_name = 'red apple',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red apples", "redapple", "redapples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_bartlett_pear'})
SET i.canonical_name = 'red bartlett pear',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red bartlett pears", "redbartlettpear", "redbartlettpears"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_bean'})
SET i.canonical_name = 'red bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["red beans", "redbean", "redbeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_bean_paste'})
SET i.canonical_name = 'red bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["red bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_beet'})
SET i.canonical_name = 'red beet',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red beets", "redbeet", "redbeets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_bliss_potato'})
SET i.canonical_name = 'red bliss potato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red bliss potatos", "redblisspotato", "redblisspotatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_cabbage'})
SET i.canonical_name = 'red cabbage',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red cabbages", "redcabbage", "redcabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_capsicum'})
SET i.canonical_name = 'red capsicum',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["red capsicums", "redcapsicum", "redcapsicums"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_chard'})
SET i.canonical_name = 'red chard',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red chards", "redchard", "redchards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_chili_pepper'})
SET i.canonical_name = 'red chili pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red chili peppers", "redchilipepper", "redchilipeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_chili_powder'})
SET i.canonical_name = 'red chili powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["red chili powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_currant'})
SET i.canonical_name = 'red currant',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red currants", "redcurrant", "redcurrants"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_curry_paste'})
SET i.canonical_name = 'red curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["red curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_delicious_apple'})
SET i.canonical_name = 'red delicious apple',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red delicious apples", "reddeliciousapple", "reddeliciousapples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_drum'})
SET i.canonical_name = 'red drum',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["red drums", "reddrum", "reddrums"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_enchilada_sauce'})
SET i.canonical_name = 'red enchilada sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["red enchilada sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_grape'})
SET i.canonical_name = 'red grape',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red grapes", "redgrape", "redgrapes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_grapefruit'})
SET i.canonical_name = 'red grapefruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red grapefruits", "redgrapefruit", "redgrapefruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_grapefruit_juice'})
SET i.canonical_name = 'red grapefruit juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["red grapefruit juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_horseradish'})
SET i.canonical_name = 'red horseradish',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["red horseradishes", "redhorseradish", "redhorseradishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_jalapeno_pepper'})
SET i.canonical_name = 'red jalapeno pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red jalapeno peppers", "redjalapenopepper", "redjalapenopeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_kidney_bean'})
SET i.canonical_name = 'red kidney bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["red kidney beans", "redkidneybean", "redkidneybeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_leaf_lettuce'})
SET i.canonical_name = 'red leaf lettuce',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["red leaf lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_lentil'})
SET i.canonical_name = 'red lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["red lentils", "redlentil", "redlentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_miso'})
SET i.canonical_name = 'red miso',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["red misos", "redmiso", "redmisos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_mullet'})
SET i.canonical_name = 'red mullet',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["red mullets", "redmullet", "redmullets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_mustard'})
SET i.canonical_name = 'red mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["red mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_onion'})
SET i.canonical_name = 'red onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red onions", "redonion", "redonions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_pepper'})
SET i.canonical_name = 'red pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red peppers", "redpepper", "redpeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_pepper_flak'})
SET i.canonical_name = 'red pepper flak',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red pepper flaks", "redpepperflak", "redpepperflaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_pepper_hot_sauce'})
SET i.canonical_name = 'red pepper hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["red pepper hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_potato'})
SET i.canonical_name = 'red potato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red potatos", "redpotato", "redpotatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_preserved_bean_curd'})
SET i.canonical_name = 'red preserved bean curd',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["red preserved bean curds", "redpreservedbeancurd", "redpreservedbeancurds"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_quinoa'})
SET i.canonical_name = 'red quinoa',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["red quinoas", "redquinoa", "redquinoas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_radish'})
SET i.canonical_name = 'red radish',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red radishes", "redradish", "redradishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_raspberry'})
SET i.canonical_name = 'red raspberry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["red raspberries", "redraspberries", "redraspberry"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_rice'})
SET i.canonical_name = 'red rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["red rices", "redrice", "redrices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_rice_vinegar'})
SET i.canonical_name = 'red rice vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["red rice vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_serrano_pepper'})
SET i.canonical_name = 'red serrano pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["red serrano peppers", "redserranopepper", "redserranopeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_snapper'})
SET i.canonical_name = 'red snapper',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["red snappers", "redsnapper", "redsnappers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_sockeye'})
SET i.canonical_name = 'red sockeye',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["red sockeyes", "redsockeye", "redsockeyes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_vermouth'})
SET i.canonical_name = 'red vermouth',
    i.category = 'beverage',
    i.base = 'vermouth',
    i.alt_names = ["red vermouths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_vinegar'})
SET i.canonical_name = 'red vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["red vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_wine'})
SET i.canonical_name = 'red wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["red wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_wine_vinaigrette'})
SET i.canonical_name = 'red wine vinaigrette',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["red wine vinaigrettes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_red_wine_vinegar'})
SET i.canonical_name = 'red wine vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["red wine vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_redhot'})
SET i.canonical_name = 'redhot',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["red hot", "red hots", "redhots"],
    i.variations = '{"other": ["redhot"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_relish'})
SET i.canonical_name = 'relish',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["relishes"],
    i.variations = '{"other": ["relish"], "grade_style": ["sweet pickle relish", "sweet relish"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rhubarb'})
SET i.canonical_name = 'rhubarb',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["rhubarbs"],
    i.variations = '{"other": ["rhubarb"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ribeye'})
SET i.canonical_name = 'ribeye',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["ribeyes"],
    i.variations = '{"other": ["ribeye"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rice'})
SET i.canonical_name = 'rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["rices"],
    i.variations = '{"other": ["fried rice", "instant rice", "instant white rice", "rice", "rice stick", "steamed brown rice", "steamed rice", "steamed white rice"], "grade_style": ["sweet rice"], "cut_or_form": ["whole grain rice"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rice_bran'})
SET i.canonical_name = 'rice bran',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["rice brans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_bran_oil'})
SET i.canonical_name = 'rice bran oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["rice bran oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_cak'})
SET i.canonical_name = 'rice cak',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["rice caks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_cracker'})
SET i.canonical_name = 'rice cracker',
    i.category = 'grain',
    i.base = 'cracker',
    i.alt_names = ["rice crackers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_flour'})
SET i.canonical_name = 'rice flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["rice flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_krispies_cereal'})
SET i.canonical_name = 'rice krispies cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["rice krispies cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_milk'})
SET i.canonical_name = 'rice milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["rice milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_noodle'})
SET i.canonical_name = 'rice noodle',
    i.category = 'grain',
    i.base = 'noodle',
    i.alt_names = ["rice noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_paddy_herb'})
SET i.canonical_name = 'rice paddy herb',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["rice paddy herbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_paper'})
SET i.canonical_name = 'rice paper',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["rice papers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_pilaf'})
SET i.canonical_name = 'rice pilaf',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["rice pilafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_powder'})
SET i.canonical_name = 'rice powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["rice powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_syrup'})
SET i.canonical_name = 'rice syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["rice syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_vermicelli'})
SET i.canonical_name = 'rice vermicelli',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["rice vermicellis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_vinegar'})
SET i.canonical_name = 'rice vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["rice vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rice_wine'})
SET i.canonical_name = 'rice wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["rice wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ricotta_cheese'})
SET i.canonical_name = 'ricotta cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["ricotta cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rigatoni'})
SET i.canonical_name = 'rigatoni',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["rigatonis"],
    i.variations = '{"other": ["rigatoni", "uncooked rigatoni"], "cut_or_form": ["dried rigatoni", "whole wheat rigatoni"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ripe_olive'})
SET i.canonical_name = 'ripe olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["ripe olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_risotto_rice'})
SET i.canonical_name = 'risotto rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["risotto rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ritz_cracker'})
SET i.canonical_name = 'ritz cracker',
    i.category = 'grain',
    i.base = 'cracker',
    i.alt_names = ["ritz crackers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_roast_beef'})
SET i.canonical_name = 'roast beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["roast beefs"],
    i.variations = null;

// Progress: 1800/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_roast_beef_deli_meat'})
SET i.canonical_name = 'roast beef deli meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["roast beef deli meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_roast_duck_meat'})
SET i.canonical_name = 'roast duck meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["roast duck meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_roast_red_peppers_drain'})
SET i.canonical_name = 'roast red peppers, drain',
    i.category = 'seafood',
    i.base = 'red',
    i.alt_names = ["roast red peppers, drains"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rock_candy_syrup'})
SET i.canonical_name = 'rock candy syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["rock candy syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rock_salt'})
SET i.canonical_name = 'rock salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["rock salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rock_shrimp'})
SET i.canonical_name = 'rock shrimp',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["rock shrimps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rock_sugar'})
SET i.canonical_name = 'rock sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["rock sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rocket_leaf'})
SET i.canonical_name = 'rocket leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["rocket leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_roll'})
SET i.canonical_name = 'roll',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["rolls"],
    i.variations = '{"other": ["roll", "spring roll", "spring roll skin", "spring roll wrapper"], "cut_or_form": ["whole grain roll"], "grade_style": ["hawaiian sweet roll"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rolled_oats'})
SET i.canonical_name = 'rolled oats',
    i.category = 'grain',
    i.base = 'oats',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_roma_tomato'})
SET i.canonical_name = 'roma tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["roma tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_romaine_lettuce'})
SET i.canonical_name = 'romaine lettuce',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["romaine lettuces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_romaine_lettuce_heart'})
SET i.canonical_name = 'romaine lettuce heart',
    i.category = 'vegetable',
    i.base = 'lettuce',
    i.alt_names = ["romaine lettuce hearts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_romaine_lettuce_leaf'})
SET i.canonical_name = 'romaine lettuce leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["romaine lettuce leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rome_apple'})
SET i.canonical_name = 'rome apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["rome apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ronzoni_penne_rigate'})
SET i.canonical_name = 'ronzoni penne rigate',
    i.category = 'grain',
    i.base = 'penne',
    i.alt_names = ["ronzoni penne rigates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_roquefort_cheese'})
SET i.canonical_name = 'roquefort cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["roquefort cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rose_leaf'})
SET i.canonical_name = 'rose leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["rose leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rose_syrup'})
SET i.canonical_name = 'rose syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["rose syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rosemary'})
SET i.canonical_name = 'rosemary',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["rosemaries"],
    i.variations = '{"other": ["rosemary"], "cut_or_form": ["dried rosemary"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rosemary_leaf'})
SET i.canonical_name = 'rosemary leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["rosemary leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ros_wine'})
SET i.canonical_name = 'rosé wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["rosé wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rotini'})
SET i.canonical_name = 'rotini',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["rotinis"],
    i.variations = '{"other": ["rotini"], "cut_or_form": ["whole grain rotini", "whole wheat rotini"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rub'})
SET i.canonical_name = 'rub',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["rubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ruby_red_grapefruit'})
SET i.canonical_name = 'ruby red grapefruit',
    i.category = 'fruit',
    i.base = 'grapefruit',
    i.alt_names = ["ruby red grapefruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rum_raisin_ice_cream'})
SET i.canonical_name = 'rum raisin ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["rum raisin ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rum_syrup'})
SET i.canonical_name = 'rum syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["rum syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_runny_honey'})
SET i.canonical_name = 'runny honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["runny honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rustic_bread'})
SET i.canonical_name = 'rustic bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["rustic breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rutabaga'})
SET i.canonical_name = 'rutabaga',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["rutabagas"],
    i.variations = '{"other": ["rutabaga"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rye'})
SET i.canonical_name = 'rye',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["ryes"],
    i.variations = '{"other": ["rye"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_rye_bread'})
SET i.canonical_name = 'rye bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["rye breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rye_flour'})
SET i.canonical_name = 'rye flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["rye flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rye_meal'})
SET i.canonical_name = 'rye meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["rye meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_rye_whiskey'})
SET i.canonical_name = 'rye whiskey',
    i.category = 'beverage',
    i.base = 'whiskey',
    i.alt_names = ["rye whiskeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_safflower_oil'})
SET i.canonical_name = 'safflower oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["safflower oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_saffron_powder'})
SET i.canonical_name = 'saffron powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["saffron powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_saffron_road_vegetable_broth'})
SET i.canonical_name = 'saffron road vegetable broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["saffron road vegetable broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sage'})
SET i.canonical_name = 'sage',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["sages"],
    i.variations = '{"other": ["sage"], "cut_or_form": ["dried sage"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sage_leaf'})
SET i.canonical_name = 'sage leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["sage leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sake'})
SET i.canonical_name = 'sake',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["sakes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salami'})
SET i.canonical_name = 'salami',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["salamis"],
    i.variations = '{"product": ["salami"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_salmon'})
SET i.canonical_name = 'salmon',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["salmons"],
    i.variations = '{"other": ["salmon"], "cut_or_form": ["canned salmon", "cold-smoked salmon", "fresh salmon", "skin on salmon fillet", "smoked salmon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_salmon_caviar'})
SET i.canonical_name = 'salmon caviar',
    i.category = 'seafood',
    i.base = 'caviar',
    i.alt_names = ["salmon caviars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salmon_fillet'})
SET i.canonical_name = 'salmon fillet',
    i.category = 'seafood',
    i.base = 'salmon',
    i.alt_names = ["salmon fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salmon_roe'})
SET i.canonical_name = 'salmon roe',
    i.category = 'seafood',
    i.base = 'salmon',
    i.alt_names = ["salmon roes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salmon_sashimi'})
SET i.canonical_name = 'salmon sashimi',
    i.category = 'seafood',
    i.base = 'salmon',
    i.alt_names = ["salmon sashimis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salmon_steak'})
SET i.canonical_name = 'salmon steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["salmon steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salsa'})
SET i.canonical_name = 'salsa',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["salsas"],
    i.variations = '{"other": ["prepar salsa"], "nutrition": ["bottled low sodium salsa"], "cut_or_form": ["fresh tomato salsa"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_salsa_verde'})
SET i.canonical_name = 'salsa verde',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["salsa verdes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salt'})
SET i.canonical_name = 'salt',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["salts"],
    i.variations = '{"other": ["salt"], "cut_or_form": ["smoked sea salt"], "nutrition": ["low sodium salt"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_salt_pork'})
SET i.canonical_name = 'salt pork',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["salt porks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_salt_water'})
SET i.canonical_name = 'salt water',
    i.category = 'beverage',
    i.base = 'water',
    i.alt_names = ["salt waters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_saltine_crumb'})
SET i.canonical_name = 'saltine crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["saltine crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sambhar_powder'})
SET i.canonical_name = 'sambhar powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["sambhar powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sanding_sugar'})
SET i.canonical_name = 'sanding sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["sanding sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sandwich_bread'})
SET i.canonical_name = 'sandwich bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["sandwich breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sardin'})
SET i.canonical_name = 'sardin',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["sardins"],
    i.variations = '{"other": ["sardin"], "cut_or_form": ["dried sardin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sashimi_grade_tuna'})
SET i.canonical_name = 'sashimi grade tuna',
    i.category = 'seafood',
    i.base = 'tuna',
    i.alt_names = ["sashimi grade tunas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_satsuma_juice'})
SET i.canonical_name = 'satsuma juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["satsuma juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_satsuma_orange'})
SET i.canonical_name = 'satsuma orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["satsuma oranges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sauce'})
SET i.canonical_name = 'sauce',
    i.category = 'sauce',
    i.base = null,
    i.alt_names = ["sauces"],
    i.variations = '{"other": ["bottled chili sauce", "cayenne pepper sauce", "chuno sauce", "gluten free soy sauce", "lea & perrins worcestershire sauce", "less sodium soy sauce", "lower sodium soy sauce", "prepared pasta sauce", "ragu traditional sauce", "stir fry sauce", "tamari soy sauce", "usukuchi soy sauce", "vegan worcestershire sauce", "wheat free soy sauce"], "flavor_source": ["mushroom soy sauce"], "nutrition": ["light alfredo sauce", "light soy sauce", "low sodium chili sauce", "low sodium pasta sauce", "low sodium soy sauce", "low sodium teriyaki sauce", "low sodium tomato sauce", "low sodium worcestershire sauce", "reduced sodium soy sauce", "reduced sodium teriyaki sauce", "reduced-sodium tamari sauce", "tomato sauce low sodium", "worcestershire sauce low sodium"], "grade_style": ["organic soy sauce", "sweet bean sauce", "sweet chili sauce", "sweet soy sauce"], "cut_or_form": ["whole cranberry sauce"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sauce_tomato'})
SET i.canonical_name = 'sauce tomato',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["sauce tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sauerkraut_juice'})
SET i.canonical_name = 'sauerkraut juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["sauerkraut juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sausage'})
SET i.canonical_name = 'sausage',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["sausages"],
    i.variations = '{"product": ["andouille chicken sausage", "sausage"], "cut_or_form": ["beef smoked sausage", "ground pork sausage", "johnsonville smoked sausage", "smoked chicken sausage", "smoked sausage"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sausage_meat'})
SET i.canonical_name = 'sausage meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["sausage meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_savoy_cabbage'})
SET i.canonical_name = 'savoy cabbage',
    i.category = 'vegetable',
    i.base = 'cabbage',
    i.alt_names = ["savoy cabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_savoy_cabbage_leaf'})
SET i.canonical_name = 'savoy cabbage leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["savoy cabbage leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_savoy_spinach'})
SET i.canonical_name = 'savoy spinach',
    i.category = 'vegetable',
    i.base = 'spinach',
    i.alt_names = ["savoy spinaches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_scallop'})
SET i.canonical_name = 'scallop',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["scallops"],
    i.variations = '{"other": ["scallop"], "cut_or_form": ["dried scallop"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_scape_pesto'})
SET i.canonical_name = 'scape pesto',
    i.category = 'condiment',
    i.base = 'pesto',
    i.alt_names = ["scape pestos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sea_bream'})
SET i.canonical_name = 'sea bream',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["sea breams", "seabream", "seabreams"],
    i.variations = '{"other": ["sea bream"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sea_cucumber'})
SET i.canonical_name = 'sea cucumber',
    i.category = 'vegetable',
    i.base = 'cucumber',
    i.alt_names = ["sea cucumbers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sea_salt'})
SET i.canonical_name = 'sea salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["sea salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sea_salt_flak'})
SET i.canonical_name = 'sea salt flak',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["sea salt flaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sea_scallop'})
SET i.canonical_name = 'sea scallop',
    i.category = 'seafood',
    i.base = 'scallop',
    i.alt_names = ["sea scallops"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seafood_stock'})
SET i.canonical_name = 'seafood stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["seafood stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seasoning'})
SET i.canonical_name = 'seasoning',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["sea soning", "sea sonings", "seasonings"],
    i.variations = '{"nutrition": ["taco seasoning reduced sodium"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_seasoning_rub'})
SET i.canonical_name = 'seasoning rub',
    i.category = 'other',
    i.base = 'rub',
    i.alt_names = ["seasoning rubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seasoning_salt'})
SET i.canonical_name = 'seasoning salt',
    i.category = 'seasoning',
    i.base = 'seasoning',
    i.alt_names = ["seasoning salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seedless_green_grape'})
SET i.canonical_name = 'seedless green grape',
    i.category = 'fruit',
    i.base = 'grape',
    i.alt_names = ["seedless green grapes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seedless_orange'})
SET i.canonical_name = 'seedless orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["seedless oranges"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seedless_raspberry_jam'})
SET i.canonical_name = 'seedless raspberry jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["seedless raspberry jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seedless_red_grap'})
SET i.canonical_name = 'seedless red grap',
    i.category = 'fruit',
    i.base = 'grap',
    i.alt_names = ["seedless red graps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_self_raising_flour'})
SET i.canonical_name = 'self raising flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["self raising flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_semi_pearled_farro'})
SET i.canonical_name = 'semi pearled farro',
    i.category = 'grain',
    i.base = 'farro',
    i.alt_names = ["semi pearled farros"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_semi_soft_cheese'})
SET i.canonical_name = 'semi-soft cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["semi-soft cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_semisweet_chocolate'})
SET i.canonical_name = 'semisweet chocolate',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["semisweet chocolates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_semisweet_chocolate_chunk'})
SET i.canonical_name = 'semisweet chocolate chunk',
    i.category = 'dairy',
    i.base = 'chocolate',
    i.alt_names = ["semisweet chocolate chunks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_semolina'})
SET i.canonical_name = 'semolina',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["semolinas"],
    i.variations = '{"other": ["semolina"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_semolina_flour'})
SET i.canonical_name = 'semolina flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["semolina flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame'})
SET i.canonical_name = 'sesame',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["sesames"],
    i.variations = '{"other": ["sesame"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_butter'})
SET i.canonical_name = 'sesame butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["sesame butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_chili_oil'})
SET i.canonical_name = 'sesame chili oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["sesame chili oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_oil'})
SET i.canonical_name = 'sesame oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["sesame oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_paste'})
SET i.canonical_name = 'sesame paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["sesame pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_salt'})
SET i.canonical_name = 'sesame salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["sesame salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_seed_paste'})
SET i.canonical_name = 'sesame seed paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["sesame seed pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sesame_seeds_bun'})
SET i.canonical_name = 'sesame seeds bun',
    i.category = 'nut_or_seed',
    i.base = 'sesame',
    i.alt_names = ["sesame seeds buns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_seville_orange'})
SET i.canonical_name = 'seville orange',
    i.category = 'fruit',
    i.base = 'orange',
    i.alt_names = ["seville oranges"],
    i.variations = null;

// Progress: 1900/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_seville_orange_juice'})
SET i.canonical_name = 'seville orange juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["seville orange juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shallot'})
SET i.canonical_name = 'shallot',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["shallots"],
    i.variations = '{"other": ["shallot"], "cut_or_form": ["dried shallot"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_shanghai_bok_choy'})
SET i.canonical_name = 'shanghai bok choy',
    i.category = 'vegetable',
    i.base = 'choy',
    i.alt_names = ["shanghai bok choies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shao_hsing_wine'})
SET i.canonical_name = 'shao hsing wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["shao hsing wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shaoxing_wine'})
SET i.canonical_name = 'shaoxing wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["shaoxing wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sheep_s_milk_cheese'})
SET i.canonical_name = 'sheep’s milk cheese',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["sheep’s milk cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shell_pasta'})
SET i.canonical_name = 'shell pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["shell pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sherry'})
SET i.canonical_name = 'sherry',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["sherries"],
    i.variations = '{"other": ["sherry"], "grade_style": ["sweet sherry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sherry_vinegar'})
SET i.canonical_name = 'sherry vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["sherry vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sherry_wine'})
SET i.canonical_name = 'sherry wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["sherry wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sherry_wine_vinegar'})
SET i.canonical_name = 'sherry wine vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["sherry wine vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shimeji_mushroom'})
SET i.canonical_name = 'shimeji mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["shimeji mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shiso_leaf'})
SET i.canonical_name = 'shiso leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["shiso leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shoepeg_corn'})
SET i.canonical_name = 'shoepeg corn',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["shoepeg corns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shoot'})
SET i.canonical_name = 'shoot',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["shoots"],
    i.variations = '{"other": ["shoot"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_short_pasta'})
SET i.canonical_name = 'short pasta',
    i.category = 'grain',
    i.base = 'pasta',
    i.alt_names = ["short pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_short_grain_rice'})
SET i.canonical_name = 'short-grain rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["short-grain rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shortcrust_pastry'})
SET i.canonical_name = 'shortcrust pastry',
    i.category = 'baking',
    i.base = 'pastry',
    i.alt_names = ["shortcrust pastries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shoulder_meat'})
SET i.canonical_name = 'shoulder meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["shoulder meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp'})
SET i.canonical_name = 'shrimp',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["prawn", "shrimps"],
    i.variations = '{"other": ["head on shrimp", "shell-on shrimp", "shelled shrimp", "shrimp"], "cut_or_form": ["dried shrimp", "ground dried shrimp"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_chip'})
SET i.canonical_name = 'shrimp chip',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["shrimp chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_head'})
SET i.canonical_name = 'shrimp head',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["shrimp heads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_meat'})
SET i.canonical_name = 'shrimp meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["shrimp meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_paste'})
SET i.canonical_name = 'shrimp paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["shrimp pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_powder'})
SET i.canonical_name = 'shrimp powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["shrimp powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_shell'})
SET i.canonical_name = 'shrimp shell',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["shrimp shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_stock'})
SET i.canonical_name = 'shrimp stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["shrimp stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shrimp_tail'})
SET i.canonical_name = 'shrimp tail',
    i.category = 'seafood',
    i.base = 'shrimp',
    i.alt_names = ["shrimp tails"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_shuck_corn'})
SET i.canonical_name = 'shuck corn',
    i.category = 'grain',
    i.base = 'corn',
    i.alt_names = ["shuck corns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sichuan_peppercorn_oil'})
SET i.canonical_name = 'sichuan peppercorn oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["sichuan peppercorn oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sichuanese_chili_paste'})
SET i.canonical_name = 'sichuanese chili paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["sichuanese chili pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sicilian_olive'})
SET i.canonical_name = 'sicilian olive',
    i.category = 'fruit',
    i.base = 'olive',
    i.alt_names = ["sicilian olives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_side_pork'})
SET i.canonical_name = 'side pork',
    i.category = 'meat',
    i.base = 'pork',
    i.alt_names = ["side porks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_simple_syrup'})
SET i.canonical_name = 'simple syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["simple syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_single_crust_pie'})
SET i.canonical_name = 'single crust pie',
    i.category = 'grain',
    i.base = 'crust',
    i.alt_names = ["single crust pies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sirloin'})
SET i.canonical_name = 'sirloin',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["sirloins"],
    i.variations = '{"other": ["sirloin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_snail'})
SET i.canonical_name = 'snail',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["snails"],
    i.variations = '{"other": ["snail"], "cut_or_form": ["canned snail"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_snapper'})
SET i.canonical_name = 'snapper',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["snappers"],
    i.variations = '{"other": ["snapper"], "cut_or_form": ["whole snapper"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_snow_crab'})
SET i.canonical_name = 'snow crab',
    i.category = 'seafood',
    i.base = 'crab',
    i.alt_names = ["snow crabs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_snow_pea'})
SET i.canonical_name = 'snow pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["snow peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_snow_pea_pod'})
SET i.canonical_name = 'snow pea pod',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["snow pea pods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_snow_pea_shoot'})
SET i.canonical_name = 'snow pea shoot',
    i.category = 'vegetable',
    i.base = 'shoot',
    i.alt_names = ["snow pea shoots"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soba'})
SET i.canonical_name = 'soba',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["sobas"],
    i.variations = '{"other": ["soba"], "cut_or_form": ["dried soba"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_soda_bread'})
SET i.canonical_name = 'soda bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["soda breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soft_cheese'})
SET i.canonical_name = 'soft cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["soft cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soft_corn_tortilla'})
SET i.canonical_name = 'soft corn tortilla',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["soft corn tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soft_goat_s_cheese'})
SET i.canonical_name = 'soft goat\'s cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["soft goat's cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soft_shell_clam'})
SET i.canonical_name = 'soft-shell clam',
    i.category = 'seafood',
    i.base = 'clam',
    i.alt_names = ["soft-shell clams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soft_wheat_flour'})
SET i.canonical_name = 'soft-wheat flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["soft-wheat flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sorghum'})
SET i.canonical_name = 'sorghum',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["sorghums"],
    i.variations = '{"other": ["sorghum"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sorghum_flour'})
SET i.canonical_name = 'sorghum flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["sorghum flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sorghum_molasses'})
SET i.canonical_name = 'sorghum molasses',
    i.category = 'sweetener',
    i.base = 'molasses',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sorghum_syrup'})
SET i.canonical_name = 'sorghum syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["sorghum syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soup'})
SET i.canonical_name = 'soup',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["soups"],
    i.variations = '{"other": ["golden mushroom soup"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_soup_bon'})
SET i.canonical_name = 'soup bon',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["soup bons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soup_noodle'})
SET i.canonical_name = 'soup noodle',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["soup noodles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soup_pasta'})
SET i.canonical_name = 'soup pasta',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["soup pastas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sour_cherry'})
SET i.canonical_name = 'sour cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["sour cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sour_cream'})
SET i.canonical_name = 'sour cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["sour creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sour_milk'})
SET i.canonical_name = 'sour milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["sour milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sour_orange_juice'})
SET i.canonical_name = 'sour orange juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["sour orange juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sour_pickle'})
SET i.canonical_name = 'sour pickle',
    i.category = 'condiment',
    i.base = 'pickle',
    i.alt_names = ["sour pickles"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sour_salt'})
SET i.canonical_name = 'sour salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["sour salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sourdough_bread'})
SET i.canonical_name = 'sourdough bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["sourdough breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soursop'})
SET i.canonical_name = 'soursop',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["soursops"],
    i.variations = '{"other": ["soursop"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_soy'})
SET i.canonical_name = 'soy',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["soies", "soya"],
    i.variations = '{"other": ["soy"], "grade_style": ["sweet soy"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_soy_bean_paste'})
SET i.canonical_name = 'soy bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["soy bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soy_marinade'})
SET i.canonical_name = 'soy marinade',
    i.category = 'condiment',
    i.base = 'marinade',
    i.alt_names = ["soy marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soy_milk'})
SET i.canonical_name = 'soy milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["soy milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soy_paste'})
SET i.canonical_name = 'soy paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["soy pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soy_sauce'})
SET i.canonical_name = 'soy sauce',
    i.category = 'sauce',
    i.base = null,
    i.alt_names = ["soy sauces", "soysauce", "soysauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soy_yogurt'})
SET i.canonical_name = 'soy yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["soy yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soya_bean'})
SET i.canonical_name = 'soya bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["soya beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soya_cheese'})
SET i.canonical_name = 'soya cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["soya cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soya_flour'})
SET i.canonical_name = 'soya flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["soya flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soybean'})
SET i.canonical_name = 'soybean',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["soybeans"],
    i.variations = '{"other": ["soybean"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_soybean_oil'})
SET i.canonical_name = 'soybean oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["soybean oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_soybean_sprout'})
SET i.canonical_name = 'soybean sprout',
    i.category = 'vegetable',
    i.base = 'sprout',
    i.alt_names = ["soybean sprouts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spaghetti'})
SET i.canonical_name = 'spaghetti',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["spaghettis"],
    i.variations = '{"other": ["spaghetti"], "cut_or_form": ["whole grain thin spaghetti", "whole wheat spaghetti", "whole wheat thin spaghetti"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_spaghetti_squash'})
SET i.canonical_name = 'spaghetti squash',
    i.category = 'vegetable',
    i.base = 'squash',
    i.alt_names = ["spaghetti squashes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_special_k_cereal'})
SET i.canonical_name = 'special k cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["special k cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spelt'})
SET i.canonical_name = 'spelt',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["spelts"],
    i.variations = '{"other": ["spelt"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_spelt_flour'})
SET i.canonical_name = 'spelt flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["spelt flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spice'})
SET i.canonical_name = 'spice',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["spices"],
    i.variations = '{"other": ["five spice"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_spicy_brown_mustard'})
SET i.canonical_name = 'spicy brown mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["spicy brown mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spicy_mayonnaise'})
SET i.canonical_name = 'spicy mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["spicy mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spicy_pork_sausage'})
SET i.canonical_name = 'spicy pork sausage',
    i.category = 'meat',
    i.base = 'sausage',
    i.alt_names = ["spicy pork sausages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spinach'})
SET i.canonical_name = 'spinach',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["spinaches"],
    i.variations = '{"other": ["baby spinach", "creamed spinach", "spinach"], "cut_or_form": ["fresh leav spinach", "fresh spinach", "frozen spinach"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_spinach_leaf'})
SET i.canonical_name = 'spinach leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["spinach leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spinach_tortilla'})
SET i.canonical_name = 'spinach tortilla',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["spinach tortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_split_black_lentil'})
SET i.canonical_name = 'split black lentil',
    i.category = 'plant_protein',
    i.base = 'lentil',
    i.alt_names = ["split black lentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_split_pea'})
SET i.canonical_name = 'split pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["split peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_split_yellow_lentil'})
SET i.canonical_name = 'split yellow lentil',
    i.category = 'plant_protein',
    i.base = 'lentil',
    i.alt_names = ["split yellow lentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_spring_onion'})
SET i.canonical_name = 'spring onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["spring onions", "springonion", "springonions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sprout'})
SET i.canonical_name = 'sprout',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["sprouts"],
    i.variations = '{"other": ["sprout"], "cut_or_form": ["fresh brussels sprout", "frozen brussels sprout"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_squash'})
SET i.canonical_name = 'squash',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["squashes"],
    i.variations = '{"other": ["squash"], "grade_style": ["sweet potato squash"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_squirrel'})
SET i.canonical_name = 'squirrel',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["squirrels"],
    i.variations = '{"other": ["squirrel"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sriracha'})
SET i.canonical_name = 'sriracha',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["srirachas"],
    i.variations = '{"other": ["sriracha"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_star_fruit'})
SET i.canonical_name = 'star fruit',
    i.category = 'fruit',
    i.base = 'fruit',
    i.alt_names = ["star fruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_starch'})
SET i.canonical_name = 'starch',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["starches"],
    i.variations = '{"grade_style": ["sweet potato starch"]}';

// Progress: 2000/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_steak'})
SET i.canonical_name = 'steak',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["steaks"],
    i.variations = '{"other": ["steak"], "cut_or_form": ["boneless beef round steak", "boneless beef sirloin steak", "fresh tuna steak"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_steak_sauce'})
SET i.canonical_name = 'steak sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["steak sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stem_ginger'})
SET i.canonical_name = 'stem ginger',
    i.category = 'seasoning',
    i.base = 'ginger',
    i.alt_names = ["stem gingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stevia_powder'})
SET i.canonical_name = 'stevia powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["stevia powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stew'})
SET i.canonical_name = 'stew',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["stews"],
    i.variations = '{"other": ["stew"], "cut_or_form": ["beef boneless meat stew"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_stew_meat'})
SET i.canonical_name = 'stew meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["stew meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stewed_tomato'})
SET i.canonical_name = 'stewed tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["stewed tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stewing_beef'})
SET i.canonical_name = 'stewing beef',
    i.category = 'meat',
    i.base = 'beef',
    i.alt_names = ["stewing beefs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sticky_rice'})
SET i.canonical_name = 'sticky rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["sticky rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stilton_cheese'})
SET i.canonical_name = 'stilton cheese',
    i.category = 'dairy',
    i.base = 'cheese',
    i.alt_names = ["stilton cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_stock'})
SET i.canonical_name = 'stock',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["stocks"],
    i.variations = '{"flavor_source": ["fresh chicken stock", "homemade beef stock", "homemade chicken stock", "homemade vegetable stock", "light chicken stock", "low sodium beef stock", "low sodium chicken stock", "low sodium vegetable stock", "organic vegetable stock", "reduced sodium beef stock", "reduced sodium chicken stock", "reduced sodium vegetable stock", "rich chicken stock", "sodium free chicken stock"], "product": ["ham stock cube"], "other": ["homemade stock"], "nutrition": ["low sodium stock"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_strained_yogurt'})
SET i.canonical_name = 'strained yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["strained yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_straw_mushroom'})
SET i.canonical_name = 'straw mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["straw mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry'})
SET i.canonical_name = 'strawberry',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["strawberries"],
    i.variations = '{"other": ["strawberry"], "cut_or_form": ["dried strawberry", "freeze-dried strawberry"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_compote'})
SET i.canonical_name = 'strawberry compote',
    i.category = 'fruit',
    i.base = 'strawberry',
    i.alt_names = ["strawberry compotes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_gelatin'})
SET i.canonical_name = 'strawberry gelatin',
    i.category = 'fruit',
    i.base = 'strawberry',
    i.alt_names = ["strawberry gelatins"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_ice_cream'})
SET i.canonical_name = 'strawberry ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["strawberry ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_jam'})
SET i.canonical_name = 'strawberry jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["strawberry jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_preserve'})
SET i.canonical_name = 'strawberry preserve',
    i.category = 'fruit',
    i.base = 'strawberry',
    i.alt_names = ["strawberry preserves"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_syrup'})
SET i.canonical_name = 'strawberry syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["strawberry syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_strawberry_yogurt'})
SET i.canonical_name = 'strawberry yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["strawberry yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_success_white_rice'})
SET i.canonical_name = 'success white rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["success white rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar'})
SET i.canonical_name = 'sugar',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["sugars"],
    i.variations = '{"other": ["golden brown sugar", "golden caster sugar", "powdered sugar", "raw cane sugar", "raw sugar", "sparkling sugar", "splenda brown sugar blend", "sugar", "superfine sugar", "superfine white sugar"], "grade_style": ["organic cane sugar", "organic granulated sugar", "organic sugar", "refined sugar", "wholesome sweeteners organic sugar"], "nutrition": ["light brown muscavado sugar", "light brown sugar"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_cane'})
SET i.canonical_name = 'sugar cane',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["sugar canes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_cane_juice'})
SET i.canonical_name = 'sugar cane juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["sugar cane juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_cookie_dough'})
SET i.canonical_name = 'sugar cookie dough',
    i.category = 'grain',
    i.base = 'dough',
    i.alt_names = ["sugar cookie doughs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_cub'})
SET i.canonical_name = 'sugar cub',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["sugar cubs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_pea'})
SET i.canonical_name = 'sugar pea',
    i.category = 'vegetable',
    i.base = 'pea',
    i.alt_names = ["sugar peas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_pearl'})
SET i.canonical_name = 'sugar pearl',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["sugar pearls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugar_syrup'})
SET i.canonical_name = 'sugar syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["sugar syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sugarcane_juice'})
SET i.canonical_name = 'sugarcane juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["sugarcane juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sumac_powder'})
SET i.canonical_name = 'sumac powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["sumac powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sundae_syrup'})
SET i.canonical_name = 'sundae syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["sundae syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sunflower_kernel'})
SET i.canonical_name = 'sunflower kernel',
    i.category = 'grain',
    i.base = 'kernel',
    i.alt_names = ["sunflower kernels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sunflower_oil'})
SET i.canonical_name = 'sunflower oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["sunflower oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sunflower_seed_butter'})
SET i.canonical_name = 'sunflower seed butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["sunflower seed butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sushi_grade_tuna'})
SET i.canonical_name = 'sushi grade tuna',
    i.category = 'seafood',
    i.base = 'tuna',
    i.alt_names = ["sushi grade tunas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sushi_rice'})
SET i.canonical_name = 'sushi rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["sushi rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sushi_vinegar'})
SET i.canonical_name = 'sushi vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["sushi vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sweet_gherkin'})
SET i.canonical_name = 'sweet gherkin',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["sweet gherkins", "sweetgherkin", "sweetgherkins"],
    i.variations = '{"grade_style": ["sweet gherkin"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_sweet_potato'})
SET i.canonical_name = 'sweet potato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["sweet potatos", "sweetpotato", "sweetpotatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_sweet_potatoes_yam'})
SET i.canonical_name = 'sweet potatoes & yam',
    i.category = 'vegetable',
    i.base = 'yam',
    i.alt_names = ["sweet potatoes & yams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_syrup'})
SET i.canonical_name = 'syrup',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["syrups"],
    i.variations = '{"other": ["golden syrup"], "nutrition": ["light corn syrup", "light pancake syrup", "light syrup"], "grade_style": ["pure maple syrup"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_szechuan_sauce'})
SET i.canonical_name = 'szechuan sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["szechuan sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_table_cream'})
SET i.canonical_name = 'table cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["table creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_table_salt'})
SET i.canonical_name = 'table salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["table salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_table_syrup'})
SET i.canonical_name = 'table syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["table syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_table_wine'})
SET i.canonical_name = 'table wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["table wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_taco_meat'})
SET i.canonical_name = 'taco meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["taco meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_taco_sauce'})
SET i.canonical_name = 'taco sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["taco sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tagliatelle'})
SET i.canonical_name = 'tagliatelle',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["tagliatelles"],
    i.variations = '{"other": ["tagliatelle"], "cut_or_form": ["dried tagliatelle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tahini_paste'})
SET i.canonical_name = 'tahini paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["tahini pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_taiwanese_bok_choy'})
SET i.canonical_name = 'taiwanese bok choy',
    i.category = 'vegetable',
    i.base = 'choy',
    i.alt_names = ["taiwanese bok choies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tamari'})
SET i.canonical_name = 'tamari',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["tamaris"],
    i.variations = '{"other": ["tamari"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tamarind_juice'})
SET i.canonical_name = 'tamarind juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["tamarind juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tamarind_paste'})
SET i.canonical_name = 'tamarind paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["tamarind pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tandoori_paste'})
SET i.canonical_name = 'tandoori paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["tandoori pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tangerine'})
SET i.canonical_name = 'tangerine',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["tangerines"],
    i.variations = '{"other": ["tangerine"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tangerine_juice'})
SET i.canonical_name = 'tangerine juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["tangerine juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tangerine_zest'})
SET i.canonical_name = 'tangerine zest',
    i.category = 'fruit',
    i.base = 'tangerine',
    i.alt_names = ["tangerine zests"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tapatio_hot_sauce'})
SET i.canonical_name = 'tapatio hot sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tapatio hot sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tapioca_flour'})
SET i.canonical_name = 'tapioca flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["tapioca flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_taro_leaf'})
SET i.canonical_name = 'taro leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["taro leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tarragon_leaf'})
SET i.canonical_name = 'tarragon leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["tarragon leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tarragon_vinegar'})
SET i.canonical_name = 'tarragon vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["tarragon vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tart_apple'})
SET i.canonical_name = 'tart apple',
    i.category = 'fruit',
    i.base = 'apple',
    i.alt_names = ["tart apples"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tart_cherry'})
SET i.canonical_name = 'tart cherry',
    i.category = 'fruit',
    i.base = 'cherry',
    i.alt_names = ["tart cherries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tartar_sauce'})
SET i.canonical_name = 'tartar sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tartar sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tea'})
SET i.canonical_name = 'tea',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["teas"],
    i.variations = '{"grade_style": ["sweet tea"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tea_cake'})
SET i.canonical_name = 'tea cake',
    i.category = 'beverage',
    i.base = 'tea',
    i.alt_names = ["tea cakes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tea_leaf'})
SET i.canonical_name = 'tea leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["tea leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_teardrop_tomato'})
SET i.canonical_name = 'teardrop tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["teardrop tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_teff'})
SET i.canonical_name = 'teff',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["teffes", "teffs", "tefves"],
    i.variations = '{"other": ["teff"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tender'})
SET i.canonical_name = 'tender',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["tenders"],
    i.variations = '{"other": ["tender"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_teriyaki_marinade'})
SET i.canonical_name = 'teriyaki marinade',
    i.category = 'condiment',
    i.base = 'marinade',
    i.alt_names = ["teriyaki marinades"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_teriyaki_sauce'})
SET i.canonical_name = 'teriyaki sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["teriyaki sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_texas_toast_bread'})
SET i.canonical_name = 'texas toast bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["texas toast breads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_thin_spaghetti'})
SET i.canonical_name = 'thin spaghetti',
    i.category = 'grain',
    i.base = 'spaghetti',
    i.alt_names = ["thin spaghettis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_thyme'})
SET i.canonical_name = 'thyme',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["thymes"],
    i.variations = '{"other": ["thyme"], "cut_or_form": ["dried thyme"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_thyme_leaf'})
SET i.canonical_name = 'thyme leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["thyme leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ti_leaf'})
SET i.canonical_name = 'ti leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["ti leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tikka_masala_curry_paste'})
SET i.canonical_name = 'tikka masala curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["tikka masala curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tikka_paste'})
SET i.canonical_name = 'tikka paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["tikka pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_toffee_sauce'})
SET i.canonical_name = 'toffee sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["toffee sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tofu_mayonnaise'})
SET i.canonical_name = 'tofu mayonnaise',
    i.category = 'condiment',
    i.base = 'mayonnaise',
    i.alt_names = ["tofu mayonnaises"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tofu_sour_cream'})
SET i.canonical_name = 'tofu sour cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["tofu sour creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tom_yum_paste'})
SET i.canonical_name = 'tom yum paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["tom yum pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomatillo_salsa'})
SET i.canonical_name = 'tomatillo salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["tomatillo salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato'})
SET i.canonical_name = 'tomato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["tomatoes", "tomatos"],
    i.variations = '{"other": ["san marzano tomato", "tomato", "tomato purée"], "cut_or_form": ["canned tomato", "dried tomato", "fresh tomato", "roasted tomato", "sun-dried tomato"], "grade_style": ["organic tomato"], "nutrition": ["low sodium tomato"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_basil_feta'})
SET i.canonical_name = 'tomato basil feta',
    i.category = 'dairy',
    i.base = 'feta',
    i.alt_names = ["tomato basil fetas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_basil_sauce'})
SET i.canonical_name = 'tomato basil sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tomato basil sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_chutney'})
SET i.canonical_name = 'tomato chutney',
    i.category = 'condiment',
    i.base = 'chutney',
    i.alt_names = ["tomato chutneies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_couli'})
SET i.canonical_name = 'tomato couli',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["tomato coulis"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_cream_sauce'})
SET i.canonical_name = 'tomato cream sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tomato cream sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_garlic_pasta_sauce'})
SET i.canonical_name = 'tomato garlic pasta sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tomato garlic pasta sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_jam'})
SET i.canonical_name = 'tomato jam',
    i.category = 'condiment',
    i.base = 'jam',
    i.alt_names = ["tomato jams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_juice'})
SET i.canonical_name = 'tomato juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["tomato juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_ketchup'})
SET i.canonical_name = 'tomato ketchup',
    i.category = 'condiment',
    i.base = 'ketchup',
    i.alt_names = ["tomato ketchups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_salsa'})
SET i.canonical_name = 'tomato salsa',
    i.category = 'condiment',
    i.base = 'salsa',
    i.alt_names = ["tomato salsas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tomato_sauce'})
SET i.canonical_name = 'tomato sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tomato sauces"],
    i.variations = null;

// Progress: 2100/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_tomato_soup'})
SET i.canonical_name = 'tomato soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["tomato soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tonkatsu_sauce'})
SET i.canonical_name = 'tonkatsu sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["tonkatsu sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tortellini'})
SET i.canonical_name = 'tortellini',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["tortellinis"],
    i.variations = '{"other": ["meat-filled tortellini", "tortellini"], "cut_or_form": ["whole wheat cheese tortellini"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tortilla'})
SET i.canonical_name = 'tortilla',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["tortillas"],
    i.variations = '{"other": ["tortilla"], "cut_or_form": ["whole wheat tortilla"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tortilla_bowl'})
SET i.canonical_name = 'tortilla bowl',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["tortilla bowls"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tortilla_chip'})
SET i.canonical_name = 'tortilla chip',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["tortilla chips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tortilla_shell'})
SET i.canonical_name = 'tortilla shell',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["tortilla shells"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tortilla_wrap'})
SET i.canonical_name = 'tortilla wrap',
    i.category = 'grain',
    i.base = 'tortilla',
    i.alt_names = ["tortilla wraps"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_treviso_radicchio'})
SET i.canonical_name = 'treviso radicchio',
    i.category = 'vegetable',
    i.base = 'radicchio',
    i.alt_names = ["treviso radicchios"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tricolor_quinoa'})
SET i.canonical_name = 'tricolor quinoa',
    i.category = 'grain',
    i.base = 'quinoa',
    i.alt_names = ["tricolor quinoas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_trout'})
SET i.canonical_name = 'trout',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["trouts"],
    i.variations = '{"other": ["trout"], "cut_or_form": ["smoked trout"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_trout_caviar'})
SET i.canonical_name = 'trout caviar',
    i.category = 'seafood',
    i.base = 'caviar',
    i.alt_names = ["trout caviars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_trout_fillet'})
SET i.canonical_name = 'trout fillet',
    i.category = 'seafood',
    i.base = 'trout',
    i.alt_names = ["trout fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_truffle_butter'})
SET i.canonical_name = 'truffle butter',
    i.category = 'dairy',
    i.base = 'butter',
    i.alt_names = ["truffle butters"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_truffle_oil'})
SET i.canonical_name = 'truffle oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["truffle oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_truffle_salt'})
SET i.canonical_name = 'truffle salt',
    i.category = 'seasoning',
    i.base = 'salt',
    i.alt_names = ["truffle salts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tuaca_liqueur'})
SET i.canonical_name = 'tuaca liqueur',
    i.category = 'beverage',
    i.base = 'liqueur',
    i.alt_names = ["tuaca liqueurs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tuna'})
SET i.canonical_name = 'tuna',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["tunas"],
    i.variations = '{"other": ["solid white tuna", "tuna"], "nutrition": ["light tuna"], "cut_or_form": ["canned tuna"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_tuna_fillet'})
SET i.canonical_name = 'tuna fillet',
    i.category = 'seafood',
    i.base = 'tuna',
    i.alt_names = ["tuna fillets"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tuna_steak'})
SET i.canonical_name = 'tuna steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["tuna steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tupelo_honey'})
SET i.canonical_name = 'tupelo honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["tupelo honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_turbinado'})
SET i.canonical_name = 'turbinado',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["turbinados"],
    i.variations = '{"other": ["turbinado"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_turkey'})
SET i.canonical_name = 'turkey',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["turkeies"],
    i.variations = '{"other": ["turkey"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_turmeric'})
SET i.canonical_name = 'turmeric',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["turmerics"],
    i.variations = '{"other": ["powdered turmeric", "turmeric", "turmeric root"], "cut_or_form": ["fresh turmeric", "ground turmeric"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_turnip_green'})
SET i.canonical_name = 'turnip green',
    i.category = 'vegetable',
    i.base = 'green',
    i.alt_names = ["turnip greens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_tzatziki'})
SET i.canonical_name = 'tzatziki',
    i.category = 'sauce',
    i.base = null,
    i.alt_names = ["tzatzikis"],
    i.variations = '{"other": ["tzatziki"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_udon'})
SET i.canonical_name = 'udon',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["udons"],
    i.variations = '{"other": ["udon"], "cut_or_form": ["dried udon"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_ume_plum_vinegar'})
SET i.canonical_name = 'ume plum vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["ume plum vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_umeboshi_paste'})
SET i.canonical_name = 'umeboshi paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["umeboshi pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_umeboshi_plum_vinegar'})
SET i.canonical_name = 'umeboshi plum vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["umeboshi plum vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_umeboshi_vinegar'})
SET i.canonical_name = 'umeboshi vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["umeboshi vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_unagi_sauce'})
SET i.canonical_name = 'unagi sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["unagi sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_unbaked_pie_shell'})
SET i.canonical_name = 'unbaked pie shell',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["unbaked pie shells", "unbakedpieshell", "unbakedpieshells"],
    i.variations = '{"other": ["unbaked pie shell"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_urad_dal_split'})
SET i.canonical_name = 'urad dal split',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["urad dal splits", "uraddalsplit", "uraddalsplits"],
    i.variations = '{"other": ["urad dal split"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_vadouvan_curry'})
SET i.canonical_name = 'vadouvan curry',
    i.category = 'seasoning',
    i.base = 'curry',
    i.alt_names = ["vadouvan curries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_valencia_rice'})
SET i.canonical_name = 'valencia rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["valencia rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla'})
SET i.canonical_name = 'vanilla',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["vanillas"],
    i.variations = '{"other": ["vanilla"], "grade_style": ["pure vanilla"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_almondmilk'})
SET i.canonical_name = 'vanilla almondmilk',
    i.category = 'sweetener',
    i.base = 'vanilla',
    i.alt_names = ["vanilla almondmilks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_bean'})
SET i.canonical_name = 'vanilla bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["vanilla beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_bean_ice_cream'})
SET i.canonical_name = 'vanilla bean ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["vanilla bean ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_bean_paste'})
SET i.canonical_name = 'vanilla bean paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["vanilla bean pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_cream'})
SET i.canonical_name = 'vanilla cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["vanilla creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_custard'})
SET i.canonical_name = 'vanilla custard',
    i.category = 'sweetener',
    i.base = 'vanilla',
    i.alt_names = ["vanilla custards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_essence'})
SET i.canonical_name = 'vanilla essence',
    i.category = 'other',
    i.base = 'essence',
    i.alt_names = ["vanilla essences"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_glaze'})
SET i.canonical_name = 'vanilla glaze',
    i.category = 'condiment',
    i.base = 'glaze',
    i.alt_names = ["vanilla glazes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_ice_cream'})
SET i.canonical_name = 'vanilla ice cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["vanilla ice creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_pod'})
SET i.canonical_name = 'vanilla pod',
    i.category = 'sweetener',
    i.base = 'vanilla',
    i.alt_names = ["vanilla pods"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_powder'})
SET i.canonical_name = 'vanilla powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["vanilla powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_soy_milk'})
SET i.canonical_name = 'vanilla soy milk',
    i.category = 'dairy',
    i.base = 'milk',
    i.alt_names = ["vanilla soy milks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_sugar'})
SET i.canonical_name = 'vanilla sugar',
    i.category = 'sweetener',
    i.base = 'sugar',
    i.alt_names = ["vanilla sugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_vodka'})
SET i.canonical_name = 'vanilla vodka',
    i.category = 'beverage',
    i.base = 'vodka',
    i.alt_names = ["vanilla vodkas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_wafer'})
SET i.canonical_name = 'vanilla wafer',
    i.category = 'sweetener',
    i.base = 'vanilla',
    i.alt_names = ["vanilla wafers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_wafer_crumb'})
SET i.canonical_name = 'vanilla wafer crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["vanilla wafer crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vanilla_yogurt'})
SET i.canonical_name = 'vanilla yogurt',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["vanilla yogurts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_varnish_clam'})
SET i.canonical_name = 'varnish clam',
    i.category = 'seafood',
    i.base = 'clam',
    i.alt_names = ["varnish clams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_veal_breast'})
SET i.canonical_name = 'veal breast',
    i.category = 'meat',
    i.base = 'breast',
    i.alt_names = ["veal breasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_veal_stock'})
SET i.canonical_name = 'veal stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["veal stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable'})
SET i.canonical_name = 'vegetable',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["vegetables"],
    i.variations = '{"other": ["stir fry vegetable blend", "vegetable"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_bouillon'})
SET i.canonical_name = 'vegetable bouillon',
    i.category = 'condiment',
    i.base = 'bouillon',
    i.alt_names = ["vegetable bouillons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_broth'})
SET i.canonical_name = 'vegetable broth',
    i.category = 'condiment',
    i.base = 'broth',
    i.alt_names = ["vegetable broths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_demi_glace'})
SET i.canonical_name = 'vegetable demi-glace',
    i.category = 'vegetable',
    i.base = 'vegetable',
    i.alt_names = ["vegetable demi-glaces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_fat'})
SET i.canonical_name = 'vegetable fat',
    i.category = 'vegetable',
    i.base = 'vegetable',
    i.alt_names = ["vegetable fats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_gumbo'})
SET i.canonical_name = 'vegetable gumbo',
    i.category = 'vegetable',
    i.base = 'vegetable',
    i.alt_names = ["vegetable gumbos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_juice'})
SET i.canonical_name = 'vegetable juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["vegetable juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_juice_cocktail'})
SET i.canonical_name = 'vegetable juice cocktail',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["vegetable juice cocktails"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_oil'})
SET i.canonical_name = 'vegetable oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["vegetable oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_oil_spray'})
SET i.canonical_name = 'vegetable oil spray',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["vegetable oil spraies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_slaw'})
SET i.canonical_name = 'vegetable slaw',
    i.category = 'vegetable',
    i.base = 'vegetable',
    i.alt_names = ["vegetable slaws"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_soup'})
SET i.canonical_name = 'vegetable soup',
    i.category = 'condiment',
    i.base = 'soup',
    i.alt_names = ["vegetable soups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetable_stock'})
SET i.canonical_name = 'vegetable stock',
    i.category = 'condiment',
    i.base = 'stock',
    i.alt_names = ["vegetable stocks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetarian_chicken'})
SET i.canonical_name = 'vegetarian chicken',
    i.category = 'meat',
    i.base = 'chicken',
    i.alt_names = ["vegetarian chickens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vegetarian_oyster_sauce'})
SET i.canonical_name = 'vegetarian oyster sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["vegetarian oyster sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_venison'})
SET i.canonical_name = 'venison',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["venisons"],
    i.variations = '{"other": ["venison"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_venison_roast'})
SET i.canonical_name = 'venison roast',
    i.category = 'meat',
    i.base = 'venison',
    i.alt_names = ["venison roasts"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_venison_steak'})
SET i.canonical_name = 'venison steak',
    i.category = 'meat',
    i.base = 'steak',
    i.alt_names = ["venison steaks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vermouth'})
SET i.canonical_name = 'vermouth',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["vermouths"],
    i.variations = '{"grade_style": ["sweet vermouth"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_vidalia_onion'})
SET i.canonical_name = 'vidalia onion',
    i.category = 'vegetable',
    i.base = 'onion',
    i.alt_names = ["vidalia onions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vindaloo_paste'})
SET i.canonical_name = 'vindaloo paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["vindaloo pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vine_leaf'})
SET i.canonical_name = 'vine leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["vine leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vine_ripened_tomato'})
SET i.canonical_name = 'vine ripened tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["vine ripened tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vine_tomato'})
SET i.canonical_name = 'vine tomato',
    i.category = 'vegetable',
    i.base = 'tomato',
    i.alt_names = ["vine tomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vinegar'})
SET i.canonical_name = 'vinegar',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["vinegars"],
    i.variations = '{"other": ["aged balsamic vinegar", "distilled malt vinegar", "distilled vinegar", "nakano seasoned rice vinegar", "seasoned rice wine vinegar"], "variety": ["white distilled vinegar"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_vital_wheat_gluten'})
SET i.canonical_name = 'vital wheat gluten',
    i.category = 'grain',
    i.base = 'gluten',
    i.alt_names = ["vital wheat glutens"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vodka'})
SET i.canonical_name = 'vodka',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["vodkas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_vodka_sauce'})
SET i.canonical_name = 'vodka sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["vodka sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_walnut'})
SET i.canonical_name = 'walnut',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["walnuts"],
    i.variations = '{"other": ["walnut"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_walnut_oil'})
SET i.canonical_name = 'walnut oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["walnut oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wasabi_paste'})
SET i.canonical_name = 'wasabi paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["wasabi pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wasabi_powder'})
SET i.canonical_name = 'wasabi powder',
    i.category = 'seasoning',
    i.base = 'powder',
    i.alt_names = ["wasabi powders"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_water'})
SET i.canonical_name = 'water',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["waters"],
    i.variations = '{"other": ["spring water", "spring! water", "water"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_water_cracker'})
SET i.canonical_name = 'water cracker',
    i.category = 'grain',
    i.base = 'cracker',
    i.alt_names = ["water crackers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_water_spinach'})
SET i.canonical_name = 'water spinach',
    i.category = 'vegetable',
    i.base = 'spinach',
    i.alt_names = ["water spinaches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_watercress'})
SET i.canonical_name = 'watercress',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["water cress", "water cresses", "watercresses"],
    i.variations = '{"other": ["watercress"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_watercress_leaf'})
SET i.canonical_name = 'watercress leaf',
    i.category = 'herb',
    i.base = 'leaf',
    i.alt_names = ["watercress leafs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wax_bean'})
SET i.canonical_name = 'wax bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["wax beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat'})
SET i.canonical_name = 'wheat',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["wheats"],
    i.variations = '{"other": ["toasted wheat germ", "wheat"], "cut_or_form": ["cracked wheat", "crusty whole wheat toast", "whole wheat bread cub", "whole wheat bread slice", "whole wheat bun", "whole wheat hamburger bun", "whole wheat pasta shell", "whole wheat penne rigate", "whole wheat pita pocket", "whole wheat pita round", "whole wheat potato bun", "whole wheat spaghettini", "whole wheat submarine loave", "whole wheat tortilla wrap", "whole wheat wrap"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_beer'})
SET i.canonical_name = 'wheat beer',
    i.category = 'beverage',
    i.base = 'beer',
    i.alt_names = ["wheat beers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_berry'})
SET i.canonical_name = 'wheat berry',
    i.category = 'fruit',
    i.base = 'berry',
    i.alt_names = ["wheat berries"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_bran'})
SET i.canonical_name = 'wheat bran',
    i.category = 'grain',
    i.base = 'wheat',
    i.alt_names = ["wheat brans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_bread'})
SET i.canonical_name = 'wheat bread',
    i.category = 'grain',
    i.base = 'bread',
    i.alt_names = ["wheat breads"],
    i.variations = null;

// Progress: 2200/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_wheat_cereal'})
SET i.canonical_name = 'wheat cereal',
    i.category = 'grain',
    i.base = 'cereal',
    i.alt_names = ["wheat cereals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_cracker'})
SET i.canonical_name = 'wheat cracker',
    i.category = 'grain',
    i.base = 'cracker',
    i.alt_names = ["wheat crackers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_flour'})
SET i.canonical_name = 'wheat flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["wheat flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_germ'})
SET i.canonical_name = 'wheat germ',
    i.category = 'grain',
    i.base = 'wheat',
    i.alt_names = ["wheat germs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wheat_starch'})
SET i.canonical_name = 'wheat starch',
    i.category = 'grain',
    i.base = 'starch',
    i.alt_names = ["wheat starches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_whipping_cream'})
SET i.canonical_name = 'whipping cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["whipping creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_whipping_heavy_cream'})
SET i.canonical_name = 'whipping heavy cream',
    i.category = 'dairy',
    i.base = 'cream',
    i.alt_names = ["whipping heavy creams"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_whiskey'})
SET i.canonical_name = 'whiskey',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["whiskeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white'})
SET i.canonical_name = 'white',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["whites"],
    i.variations = '{"cut_or_form": ["fresh white truffle"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_white_almond_bark'})
SET i.canonical_name = 'white almond bark',
    i.category = 'nut_or_seed',
    i.base = null,
    i.alt_names = ["white almond barks", "whitealmondbark", "whitealmondbarks"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_arborio_rice'})
SET i.canonical_name = 'white arborio rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white arborio rices", "whitearboriorice", "whitearboriorices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_asparagus'})
SET i.canonical_name = 'white asparagus',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["white asparagu", "white asparaguses", "whiteasparagu", "whiteasparagus", "whiteasparaguses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_bean'})
SET i.canonical_name = 'white bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["white beans", "whitebean", "whitebeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_bread'})
SET i.canonical_name = 'white bread',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white breads", "whitebread", "whitebreads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_bread_crumb'})
SET i.canonical_name = 'white bread crumb',
    i.category = 'grain',
    i.base = 'crumb',
    i.alt_names = ["white bread crumbs"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_bread_flour'})
SET i.canonical_name = 'white bread flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["white bread flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_bread_slice'})
SET i.canonical_name = 'white bread slice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white bread slices", "whitebreadslice", "whitebreadslices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_button_mushroom'})
SET i.canonical_name = 'white button mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["white button mushrooms", "whitebuttonmushroom", "whitebuttonmushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_cabbage'})
SET i.canonical_name = 'white cabbage',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["white cabbages", "whitecabbage", "whitecabbages"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_cannellini_bean'})
SET i.canonical_name = 'white cannellini bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["white cannellini beans", "whitecannellinibean", "whitecannellinibeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_cheddar_cheese'})
SET i.canonical_name = 'white cheddar cheese',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["white cheddar cheeses", "whitecheddarcheese", "whitecheddarcheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_cheese'})
SET i.canonical_name = 'white cheese',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["white cheeses", "whitecheese", "whitecheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_chocolate'})
SET i.canonical_name = 'white chocolate',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["white chocolates", "whitechocolate", "whitechocolates"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_chocolate_chip'})
SET i.canonical_name = 'white chocolate chip',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["white chocolate chips", "whitechocolatechip", "whitechocolatechips"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_corn'})
SET i.canonical_name = 'white corn',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white corns", "whitecorn", "whitecorns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_corn_syrup'})
SET i.canonical_name = 'white corn syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["white corn syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_corn_tortilla'})
SET i.canonical_name = 'white corn tortilla',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white corn tortillas", "whitecorntortilla", "whitecorntortillas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_cornmeal'})
SET i.canonical_name = 'white cornmeal',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white cornmeals", "whitecornmeal", "whitecornmeals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_creme_de_cacao'})
SET i.canonical_name = 'white creme de cacao',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["white creme de cacaos", "whitecremedecacao", "whitecremedecacaos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_fleshed_fish'})
SET i.canonical_name = 'white fleshed fish',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["white fleshed fishes", "whitefleshedfish", "whitefleshedfishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_flour'})
SET i.canonical_name = 'white flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["white flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_grape_juice'})
SET i.canonical_name = 'white grape juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["white grape juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_grapefruit'})
SET i.canonical_name = 'white grapefruit',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["white grapefruits", "whitegrapefruit", "whitegrapefruits"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_grapefruit_juice'})
SET i.canonical_name = 'white grapefruit juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["white grapefruit juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_hominy'})
SET i.canonical_name = 'white hominy',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["white hominies", "whitehominies", "whitehominy"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_kidney_bean'})
SET i.canonical_name = 'white kidney bean',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["white kidney beans", "whitekidneybean", "whitekidneybeans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_lentil'})
SET i.canonical_name = 'white lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["white lentils", "whitelentil", "whitelentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_lily_flour'})
SET i.canonical_name = 'white lily flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["white lily flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_miso'})
SET i.canonical_name = 'white miso',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["white misos", "whitemiso", "whitemisos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_mushroom'})
SET i.canonical_name = 'white mushroom',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["white mushrooms", "whitemushroom", "whitemushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_onion'})
SET i.canonical_name = 'white onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["white onions", "whiteonion", "whiteonions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_peach'})
SET i.canonical_name = 'white peach',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["white peaches", "whitepeach", "whitepeaches"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_pepper'})
SET i.canonical_name = 'white pepper',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["white peppers", "whitepepper", "whitepeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_peppercorn'})
SET i.canonical_name = 'white peppercorn',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["white peppercorns", "whitepeppercorn", "whitepeppercorns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_quinoa'})
SET i.canonical_name = 'white quinoa',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white quinoas", "whitequinoa", "whitequinoas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_radish'})
SET i.canonical_name = 'white radish',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["white radishes", "whiteradish", "whiteradishes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_rice'})
SET i.canonical_name = 'white rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white rices", "whiterice", "whiterices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_rice_flour'})
SET i.canonical_name = 'white rice flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["white rice flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_rice_vinegar'})
SET i.canonical_name = 'white rice vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["white rice vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_rum'})
SET i.canonical_name = 'white rum',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["white rums", "whiterum", "whiterums"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_sandwich_bread'})
SET i.canonical_name = 'white sandwich bread',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["white sandwich breads", "whitesandwichbread", "whitesandwichbreads"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_sugar'})
SET i.canonical_name = 'white sugar',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["white sugars", "whitesugar", "whitesugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_tequila'})
SET i.canonical_name = 'white tequila',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["white tequilas", "whitetequila", "whitetequilas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_truffle_oil'})
SET i.canonical_name = 'white truffle oil',
    i.category = 'condiment',
    i.base = 'oil',
    i.alt_names = ["white truffle oils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_tuna'})
SET i.canonical_name = 'white tuna',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["white tunas", "whitetuna", "whitetunas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_vermouth'})
SET i.canonical_name = 'white vermouth',
    i.category = 'beverage',
    i.base = 'vermouth',
    i.alt_names = ["white vermouths"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_vinegar'})
SET i.canonical_name = 'white vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["white vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_wine'})
SET i.canonical_name = 'white wine',
    i.category = 'beverage',
    i.base = 'wine',
    i.alt_names = ["white wines"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_wine_vinegar'})
SET i.canonical_name = 'white wine vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["white wine vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_white_zinfandel'})
SET i.canonical_name = 'white zinfandel',
    i.category = 'seasoning',
    i.base = null,
    i.alt_names = ["white zinfandels", "whitezinfandel", "whitezinfandels"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_whitefish'})
SET i.canonical_name = 'whitefish',
    i.category = 'seafood',
    i.base = null,
    i.alt_names = ["white fish", "white fishes", "whitefishes"],
    i.variations = '{"other": ["whitefish"], "cut_or_form": ["smoked whitefish"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_wholemeal_flour'})
SET i.canonical_name = 'wholemeal flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["wholemeal flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wiener'})
SET i.canonical_name = 'wiener',
    i.category = 'meat',
    i.base = null,
    i.alt_names = ["wieners"],
    i.variations = '{"other": ["wiener"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_wild_asparagus'})
SET i.canonical_name = 'wild asparagus',
    i.category = 'vegetable',
    i.base = 'asparagus',
    i.alt_names = [],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wild_garlic'})
SET i.canonical_name = 'wild garlic',
    i.category = 'vegetable',
    i.base = 'garlic',
    i.alt_names = ["wild garlics"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wild_mushroom'})
SET i.canonical_name = 'wild mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["wild mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wild_rice'})
SET i.canonical_name = 'wild rice',
    i.category = 'grain',
    i.base = 'rice',
    i.alt_names = ["wild rices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wild_salmon'})
SET i.canonical_name = 'wild salmon',
    i.category = 'seafood',
    i.base = 'salmon',
    i.alt_names = ["wild salmons"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wildflower_honey'})
SET i.canonical_name = 'wildflower honey',
    i.category = 'sweetener',
    i.base = 'honey',
    i.alt_names = ["wildflower honeies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wine'})
SET i.canonical_name = 'wine',
    i.category = 'beverage',
    i.base = null,
    i.alt_names = ["wines"],
    i.variations = '{"other": ["dry red wine", "dry white wine", "sparkling rosé wine", "sparkling wine"], "grade_style": ["sweet rice wine", "sweet white wine"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_wine_syrup'})
SET i.canonical_name = 'wine syrup',
    i.category = 'sweetener',
    i.base = 'syrup',
    i.alt_names = ["wine syrups"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wine_vinegar'})
SET i.canonical_name = 'wine vinegar',
    i.category = 'condiment',
    i.base = 'vinegar',
    i.alt_names = ["wine vinegars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wing_sauce'})
SET i.canonical_name = 'wing sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["wing sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wondra_flour'})
SET i.canonical_name = 'wondra flour',
    i.category = 'grain',
    i.base = 'flour',
    i.alt_names = ["wondra flours"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wood_ear_mushroom'})
SET i.canonical_name = 'wood ear mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["wood ear mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_wood_mushroom'})
SET i.canonical_name = 'wood mushroom',
    i.category = 'vegetable',
    i.base = 'mushroom',
    i.alt_names = ["wood mushrooms"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_worcestershire_sauce'})
SET i.canonical_name = 'worcestershire sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["worcestershire sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yakisoba_sauce'})
SET i.canonical_name = 'yakisoba sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["yakisoba sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yam'})
SET i.canonical_name = 'yam',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yams"],
    i.variations = '{"other": ["yam"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_yam_bean'})
SET i.canonical_name = 'yam bean',
    i.category = 'plant_protein',
    i.base = 'bean',
    i.alt_names = ["yam beans"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yeast'})
SET i.canonical_name = 'yeast',
    i.category = 'baking',
    i.base = null,
    i.alt_names = ["yeasts"],
    i.variations = '{"other": ["yeast"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_bean_sauce'})
SET i.canonical_name = 'yellow bean sauce',
    i.category = 'sauce',
    i.base = 'sauce',
    i.alt_names = ["yellow bean sauces"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_chive'})
SET i.canonical_name = 'yellow chive',
    i.category = 'herb',
    i.base = null,
    i.alt_names = ["yellow chives", "yellowchive", "yellowchives"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_corn'})
SET i.canonical_name = 'yellow corn',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["yellow corns", "yellowcorn", "yellowcorns"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_corn_meal'})
SET i.canonical_name = 'yellow corn meal',
    i.category = 'grain',
    i.base = 'meal',
    i.alt_names = ["yellow corn meals"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_crookneck_squash'})
SET i.canonical_name = 'yellow crookneck squash',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow crookneck squashes", "yellowcrooknecksquash", "yellowcrooknecksquashes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_curry_paste'})
SET i.canonical_name = 'yellow curry paste',
    i.category = 'seasoning',
    i.base = 'paste',
    i.alt_names = ["yellow curry pastes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_heirloom_tomato'})
SET i.canonical_name = 'yellow heirloom tomato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow heirloom tomatos", "yellowheirloomtomato", "yellowheirloomtomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_hominy'})
SET i.canonical_name = 'yellow hominy',
    i.category = 'other',
    i.base = null,
    i.alt_names = ["yellow hominies", "yellowhominies", "yellowhominy"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_lentil'})
SET i.canonical_name = 'yellow lentil',
    i.category = 'plant_protein',
    i.base = null,
    i.alt_names = ["yellow lentils", "yellowlentil", "yellowlentils"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_miso'})
SET i.canonical_name = 'yellow miso',
    i.category = 'condiment',
    i.base = null,
    i.alt_names = ["yellow misos", "yellowmiso", "yellowmisos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_mustard'})
SET i.canonical_name = 'yellow mustard',
    i.category = 'condiment',
    i.base = 'mustard',
    i.alt_names = ["yellow mustards"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_onion'})
SET i.canonical_name = 'yellow onion',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow onions", "yellowonion", "yellowonions"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_pea'})
SET i.canonical_name = 'yellow pea',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow peas", "yellowpea", "yellowpeas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_pepper'})
SET i.canonical_name = 'yellow pepper',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow peppers", "yellowpepper", "yellowpeppers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_rice'})
SET i.canonical_name = 'yellow rice',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["yellow rices", "yellowrice", "yellowrices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_rock_sugar'})
SET i.canonical_name = 'yellow rock sugar',
    i.category = 'sweetener',
    i.base = null,
    i.alt_names = ["yellow rock sugars", "yellowrocksugar", "yellowrocksugars"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_split_pea'})
SET i.canonical_name = 'yellow split pea',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow split peas", "yellowsplitpea", "yellowsplitpeas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_squash'})
SET i.canonical_name = 'yellow squash',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow squashes", "yellowsquash", "yellowsquashes"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellow_summer_squash'})
SET i.canonical_name = 'yellow summer squash',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow summer squashes", "yellowsummersquash", "yellowsummersquashes"],
    i.variations = null;

// Progress: 2300/2311 ingredients
MERGE (i:Ingredient {ingredient_id: 'ing_yellow_tomato'})
SET i.canonical_name = 'yellow tomato',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["yellow tomatos", "yellowtomato", "yellowtomatos"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yellowfin_tuna'})
SET i.canonical_name = 'yellowfin tuna',
    i.category = 'seafood',
    i.base = 'tuna',
    i.alt_names = ["yellowfin tunas"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yogurt'})
SET i.canonical_name = 'yogurt',
    i.category = 'dairy',
    i.base = null,
    i.alt_names = ["yoghurt", "yogurts"],
    i.variations = '{"other": ["homemade yogurt", "vanilla lowfat yogurt", "vegan yogurt"], "nutrition": ["non dairy yogurt", "nonfat frozen yogurt", "nonfat vanilla frozen yogurt", "nonfat vanilla yogurt", "nonfat yogurt"], "cut_or_form": ["vanilla frozen yogurt"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_yogurt_cheese'})
SET i.canonical_name = 'yogurt cheese',
    i.category = 'dairy',
    i.base = 'yogurt',
    i.alt_names = ["yogurt cheeses"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yolk'})
SET i.canonical_name = 'yolk',
    i.category = 'baking',
    i.base = null,
    i.alt_names = ["yolks"],
    i.variations = '{"other": ["yolk"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_young_coconut_meat'})
SET i.canonical_name = 'young coconut meat',
    i.category = 'meat',
    i.base = 'meat',
    i.alt_names = ["young coconut meats"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_young_ginger'})
SET i.canonical_name = 'young ginger',
    i.category = 'seasoning',
    i.base = 'ginger',
    i.alt_names = ["young gingers"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yu_choy'})
SET i.canonical_name = 'yu choy',
    i.category = 'vegetable',
    i.base = 'choy',
    i.alt_names = ["yu choies"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_yuzu'})
SET i.canonical_name = 'yuzu',
    i.category = 'fruit',
    i.base = null,
    i.alt_names = ["yuzus"],
    i.variations = '{"other": ["yuzu"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_yuzu_juice'})
SET i.canonical_name = 'yuzu juice',
    i.category = 'beverage',
    i.base = 'juice',
    i.alt_names = ["yuzu juices"],
    i.variations = null;

MERGE (i:Ingredient {ingredient_id: 'ing_ziti'})
SET i.canonical_name = 'ziti',
    i.category = 'grain',
    i.base = null,
    i.alt_names = ["zitis"],
    i.variations = '{"other": ["ziti"], "cut_or_form": ["dried ziti"]}';

MERGE (i:Ingredient {ingredient_id: 'ing_zucchini'})
SET i.canonical_name = 'zucchini',
    i.category = 'vegetable',
    i.base = null,
    i.alt_names = ["zucchinis"],
    i.variations = '{"other": ["golden zucchini", "zucchini"]}';
