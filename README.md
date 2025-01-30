# RetailBot
Retail bot written using a modified playwright webdriver and asyncIO for ecommerce automation

# Installation
- Make sure to install chromium driver before running the bot.

```bash 
# Pip install requirements.txt
pip install -r requirements.txt
# Install Chromium-Driver for Patchright https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
patchright install chromium
```

- set up user_data.json an example is provided
- add urls and supported store name into config.json

- Run the bot!

{
"store": "BestBuy",
"target_url": "https://www.bestbuy.com/site/searchpage.jsp?st=flash+drives&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys"
},

{
"store": "BestBuy",
"target_url": "https://www.bestbuy.com/site/searchpage.jsp?id=pcat17071&qp=category_facet%3DGPUs%20%2F%20Video%20Graphics%20Cards~abcat0507002%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~Nvidia%20GeForce%20RTX%205090&st=5090+gpu"
}