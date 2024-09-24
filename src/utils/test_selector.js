const selectors = {
    "name": '//h3[@itemprop="name"]/text()',
    'category': '//div[@class="aisle-module-container"]//span[@data-testid="description-text"]/text()',
    "price": '//span[@class="product-price-new__price"]/text()',
    "image": '//ul[@class="product-preview-list"]//img/@src',
    "sku": '//div[@class="aisle-info-container"]//h4[@data-testid="aisle-number"]/text()',
    "description": '//div[@class="description"]//text()',
    "weight": '//div[@class="base-price-container"]//h5[@itemprop="price"]/text()',
    'availability': '//div[@class="stock-status-container__stock-status instock"]/text()',
    'brand': '//div[@class="aisle-module-container"]//p[@class="regular-type stock-status-store"]/text()',
    'discount_price': "//span[contains(@class, 'product-price-new__price') and contains(@class, 'product-price-new__price--discount')]/text()",
    'single_image': "//img[@itemprop='image' and @data-testid='carouselImageLarge0']/@src"
};

function extractTextContent(xpath) {
    const evaluator = new XPathEvaluator();
    const result = evaluator.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    let texts = [];
    for (let i = 0; i < result.snapshotLength; i++) {
        texts.push(result.snapshotItem(i).textContent.trim());
    }
    return texts;
}

for (let key in selectors) {
    let textContent = extractTextContent(selectors[key]);
    console.log(`${key}:`, textContent);
}
