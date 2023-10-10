import requests
from bs4 import BeautifulSoup
import pandas
import os, random 


# This app is only for this URL
homeURL = 'https://outfitterstore.nl'
# homeURL = 'https://outfitterstore.nl/product-category/sport/trainingspakken/'
# homeURL = 'https://outfitterstore.nl/product-category/accessories/socks/'
uploadsPath = './uploads'
if not os.path.exists(uploadsPath):
    os.mkdir(uploadsPath)
csvsPath = './csvs'
if not os.path.exists(csvsPath):
    os.mkdir(csvsPath)

def download_images(url):
    paths = url.split("/")
    upperdirectoryUrl = uploadsPath + "/" + paths[(len(paths)-3)]
    directoryUrl = uploadsPath + "/" + paths[(len(paths)-3)] + "/" + paths[(len(paths)-2)]
    imageUrl = uploadsPath + "/" + paths[(len(paths)-3)] + "/" + paths[(len(paths)-2)] + "/" + paths[(len(paths)-1)]
    if not os.path.exists(imageUrl) :
        if not os.path.exists(upperdirectoryUrl):
            os.mkdir(upperdirectoryUrl)
            print("Folder %s created!" % upperdirectoryUrl)
            if not os.path.exists(directoryUrl):
                os.mkdir(directoryUrl)
                print("Folder %s created!" % directoryUrl)
            else :
                pass
        elif not os.path.exists(directoryUrl):
            os.mkdir(directoryUrl)
            print("Folder %s created!" % directoryUrl)
        else:
            pass
    
        r = requests.get(url).content
        with open(imageUrl, "wb+") as f:
            f.write(r)
        print("Successfully downloaded %s" % paths[(len(paths)-1)])
    else :
        # print("Already Existed: skipped") 
        pass
    
def Start(URL) :
# def Start(url) :
    proCount = 0
    imgCount = 0
    gender = ["Men, Women", "Men", "Women"]
    URLs = []
    initPage = requests.get(URL)
    initSoup = BeautifulSoup(initPage.content, "html.parser")
    navigations = initSoup.find(id="menu-2-d21cafd").find_all('a', class_="elementor-sub-item")
    for nav in navigations : 
        # if "socks" not in nav['href'] and "bags" not in nav['href'] and "accessories" not in nav['href'] :
        #     # URLs.append([nav['href'], nav.text.strip()])
        #     pass
        # else:
        #     URLs.append([nav['href'], nav.text.strip()])
        #     # pass
        URLs.append([nav['href'], nav.text.strip()])
    for arr in URLs :
        
        cats = arr[0].split("product-category/")[1]
        categories = cats.split('/')
        rootCate = categories[0]
        subCate = arr[1]
        pro_cate = "bestsellers, new in, " + rootCate + ", " + rootCate + " > " + subCate
        filename = csvsPath + "/" + rootCate  
        for c in range(1, len(categories)-1) :
            # pro_cate = pro_cate + " > " + categories[c]
            # subCate = subCate + " > " + categories[c]
            filename = filename + "_" + categories[c]
        filename = filename + "_products.csv"
        if os.path.exists(filename) :
            print("Skipped: %s" % filename)
            pass
        else :
            url = arr[0]
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            pageURLs = [url]
            paginations = soup.find("nav", class_="ct-pagination")
            if paginations != None :
                pages = paginations.find("div").find_all("a", class_="page-numbers")
                pageCnt = int(pages[len(pages)-1].text.strip()) + 1
                for p in range(2, pageCnt):
                    pageURLs.append(url + "page/" + str(p) + "/")
            else :
                pass
            headers = []
            for p_url in pageURLs:
                page = requests.get(p_url)
                sup = BeautifulSoup(page.content, "html.parser")
                container = sup.find("ul", class_="products")
                if container == None :
                    print(f"skipped: {p_url}")
                    pass
                else :
                    products = container.find_all("li", class_="product")
                    for product in products:
                        proCount = proCount + 1
                        proC = "Products : {}"
                        print(proC.format(proCount))
                        
                        title = product.find("h2").text.strip()
                        price = product.find("span", class_="price").text.strip()
                        price = price.split()[1]
                        cart = product.find("a", class_="product_type_variable")
                        if cart == None : 
                            cart = product.find("a", class_="product_type_simple")
                            
                        pro_id = cart['data-product_id']
                        pro_url = product.find("a", class_="ct-image-container")["href"]
                        pro_page = requests.get(pro_url)
                        pro_soup = BeautifulSoup(pro_page.content, "html.parser")
                        pro_wrapper = pro_soup.find("div", class_="product-entry-wrapper")
                        if pro_wrapper == None :
                            print(pro_url)
                            pro_wrapper = pro_soup.find("div", class_="product-entry-wrapper")
                        pro_images = pro_wrapper.find_all("a", class_="ct-image-container")
                        
                        imageURL = ""
                        for img in pro_images:
                            tmp = "http://519732575.swh.strato-hosting.eu/wordpress" + img["href"].split(".nl")[1]
                            imgCount = imgCount + 1
                            download_images(img["href"])
                            # imgFilename = tmp.split("/")[(len(tmp.split("/")) - 1)]
                            # imageTitle = imgFilename.split(".")[0]
                            imgstr = "image : {}"
                            print(imgstr.format(imgCount))
                            if imageURL == "" :
                                imageURL = tmp
                            else:
                                imageURL = imageURL + ", " + tmp
                        
                        option = []
                        options = ""
                        pro_type = ""
                        variations = pro_wrapper.find('table', class_="variations")
                        if variations != None :
                            pro_type = "variable"
                            pro_label = variations.find('label').text.strip()
                            pro_size = variations.find(id="pa_size").find_all("option")
                            if len(pro_size) > 0 :
                                for psz in pro_size :
                                    if psz.text.strip() != 'Choose an option':
                                        option.append(psz.text.strip())
                                        if options == "" :
                                            options = psz.text.strip()
                                        else :
                                            options = options + ", " + psz.text.strip()
                        else :
                            pro_type = "simple"
                        
                        sku = title.split()[0] + "-" + title.split()[1] + "-" + pro_id
                        # permalink = 'http://localhost/scraping-outfitterstore/product/' + sku.lower()
                        genderid = random.randrange(0, 3)
                        if pro_type == 'variable' :    
                            headers.append({
                                'ID': pro_id,
                                'Type': pro_type, 
                                'SKU': sku,
                                'Name': title, 
                                'Published': 1, 
                                'Is featured?': 0, 
                                'Visibility in catalog': 'visible', 
                                'Short description': '🚚 Besteld voor 23:00 = <strong>Vandaag</strong> ingepakt en verzonden\n🔎 Alle bestellingen zijn voorzien van <strong>Track</strong> <strong>&amp;</strong> <strong>Trace</strong>\n📞 <strong>24/7 klantenservice</strong> via whatsapp (Reactietijd - <strong>5/10 min</strong>)', 
                                'Description': '', 
                                'Date sale price starts': '', 
                                'Date sale price ends': '', 
                                'Tax status': 'taxable', 
                                'Tax class': '', 
                                'In stock?': 1, 
                                'Stock': '', 
                                'Low stock': '', 
                                'Backorder allowed?': 0, 
                                'Sold individually?': 0, 
                                'Weight (kg)':'', 
                                'Length (cm)':'', 
                                'Width (cm)':'', 
                                'Height (cm)':'',
                                'Allow customer reviews?': 1,
                                'Purchase note': '',
                                'regular_price': price, 
                                'sale_price': '', 
                                'Categories' : pro_cate, 
                                'Tags': '', 
                                'Shipping class': '', 
                                'Images': imageURL, 
                                'Download limit': '', 
                                'Download expiry days': '', 
                                'Parent' : '', 
                                'Grouped products' : '', 
                                'Upsells' : '', 
                                'Cross-sells' : '', 
                                'External URL' : '', 
                                'Button text' : '', 
                                'Position' : 0, 
                                'Attribute 1 name' : pro_label, 
                                'Attribute 1 value(s)' : options, 
                                'Attribute 1 visible' : 0, 
                                'Attribute 1 global' : 0, 
                                'Attribute 2 name' : 'Gender', 
                                'Attribute 2 value(s)' : gender[genderid], 
                                'Attribute 2 visible' : '', 
                                'Attribute 2 global' : 1, 
                                'Meta:product_image_on_hover' : 'yes', 
                                'Meta:custom_tab_priority1' : 40, 
                                'Meta:custom_tab_priority2' : 41, 
                                'Meta:header_view' : 'default', 
                                'Meta:layout' : 'right-sidebar', 
                                'Meta:sidebar_menu' : '', 
                                'Meta:demo_product_info' : '',
                                'Meta:product_layout' : '',
                                'Meta:_wcfm_product_views' : '', 
                                'Meta:pageview' : '',
                                'Meta: _last_editor_used_jetpack': 'classic-editor' 
                            })
                        
                            c = 1
                            for opt in option :
                                c_id = int(pro_id) * 1000 + c
                                headers.append({
                                    'ID': c_id,
                                    'Type': 'variation', 
                                    'SKU': '',
                                    'Name': title + "-" + opt, 
                                    'Published': 1, 
                                    'Is featured?': 0, 
                                    'Visibility in catalog': 'visible', 
                                    'Short description': '', 
                                    'Description': '', 
                                    'Date sale price starts': '', 
                                    'Date sale price ends': '', 
                                    'Tax status': 'taxable', 
                                    'Tax class': 'parent', 
                                    'In stock?': 1, 
                                    'Stock': '', 
                                    'Low stock': '', 
                                    'Backorder allowed?': 0, 
                                    'Sold individually?': 0, 
                                    'Weight (kg)':'', 
                                    'Length (cm)':'', 
                                    'Width (cm)':'', 
                                    'Height (cm)':'',
                                    'Allow customer reviews?': 0,
                                    'Purchase note': '',
                                    'regular_price': price, 
                                    'sale_price': '', 
                                    'Categories' : '', 
                                    'Tags': '', 
                                    'Shipping class': '', 
                                    'Images': '', 
                                    'Download limit': '', 
                                    'Download expiry days': '', 
                                    'Parent' : sku, 
                                    'Grouped products' : '', 
                                    'Upsells' : '', 
                                    'Cross-sells' : '', 
                                    'External URL' : '', 
                                    'Button text' : '', 
                                    'Position' : c, 
                                    'Attribute 1 name' : pro_label, 
                                    'Attribute 1 value(s)' : opt, 
                                    'Attribute 1 visible' : '', 
                                    'Attribute 1 global' : 0, 
                                    'Attribute 2 name' : '', 
                                    'Attribute 2 value(s)' : '', 
                                    'Attribute 2 visible' : '', 
                                    'Attribute 2 global' : '', 
                                    'Meta:product_image_on_hover' : '', 
                                    'Meta:custom_tab_priority1' : '', 
                                    'Meta:custom_tab_priority2' : '', 
                                    'Meta:header_view' : '', 
                                    'Meta:layout' : '', 
                                    'Meta:sidebar_menu' : '', 
                                    'Meta:demo_product_info' : '',
                                    'Meta:product_layout' : '', 
                                    'Meta:_wcfm_product_views' : '', 
                                    'Meta:pageview' : '',
                                    'Meta: _last_editor_used_jetpack': '' 
                                })
                                c = c + 1
                        else :
                            headers.append({
                                'ID': pro_id,
                                'Type': pro_type, 
                                'SKU': sku,
                                'Name': title, 
                                'Published': 1, 
                                'Is featured?': 0, 
                                'Visibility in catalog': 'visible', 
                                'Short description': '🚚 Besteld voor 23:00 = <strong>Vandaag</strong> ingepakt en verzonden\n🔎 Alle bestellingen zijn voorzien van <strong>Track</strong> <strong>&amp;</strong> <strong>Trace</strong>\n📞 <strong>24/7 klantenservice</strong> via whatsapp (Reactietijd - <strong>5/10 min</strong>)', 
                                'Description': '', 
                                'Date sale price starts': '', 
                                'Date sale price ends': '', 
                                'Tax status': 'taxable', 
                                'Tax class': '', 
                                'In stock?': 1, 
                                'Stock': 5, 
                                'Low stock': '', 
                                'Backorder allowed?': 0, 
                                'Sold individually?': 0, 
                                'Weight (kg)':'', 
                                'Length (cm)':'', 
                                'Width (cm)':'', 
                                'Height (cm)':'',
                                'Allow customer reviews?': 1,
                                'Purchase note': '',
                                'regular_price': price, 
                                'sale_price': '', 
                                'Categories' : pro_cate, 
                                'Tags': '', 
                                'Shipping class': '', 
                                'Images': imageURL, 
                                'Download limit': '', 
                                'Download expiry days': '', 
                                'Parent' : '', 
                                'Grouped products' : '', 
                                'Upsells' : '', 
                                'Cross-sells' : '', 
                                'External URL' : '', 
                                'Button text' : '', 
                                'Position' : 0, 
                                'Attribute 1 name' : 'Gender', 
                                'Attribute 1 value(s)' : gender[genderid], 
                                'Attribute 1 visible' : 0, 
                                'Attribute 1 global' : 1, 
                                'Attribute 2 name' : '', 
                                'Attribute 2 value(s)' : '', 
                                'Attribute 2 visible' : '', 
                                'Attribute 2 global' : '', 
                                'Meta:product_image_on_hover' : '', 
                                'Meta:custom_tab_priority1' : 40, 
                                'Meta:custom_tab_priority2' : 41, 
                                'Meta:header_view' : '', 
                                'Meta:layout' : '', 
                                'Meta:sidebar_menu' : '', 
                                'Meta:demo_product_info' : '',
                                'Meta:product_layout' : '',
                                'Meta:_wcfm_product_views' : '', 
                                'Meta:pageview' : '',
                                'Meta: _last_editor_used_jetpack': 'classic-editor'
                            })
                            
                        # print(rootCate, subCate, pro_id, title, price, pro_url, imageURL, option)
                    progress = "Successfully {} products of {}>{} category are added..."
                    print(progress.format(len(headers), rootCate, subCate))
            if len(headers) > 0 :
                data = pandas.DataFrame(headers) 
                data.to_csv(filename, index=False, encoding='utf-8-sig')
                stepDone = "Successfully all {} products of {}>{} category are saved in .csv..."
                print(stepDone.format(len(headers), rootCate, subCate))
Start(homeURL)
print("Sucessfully scraping...")

 

 
        