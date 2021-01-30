# TREETOOL #

* The purpose is to convert get information from CREO into a manageable JSON object.

### Technologies used ###

* Python 3.7.4
* CREOSON 2.5 (optional)
* CREO 3.0 (optional)

### Installation ###

* Create a subfolder in your project and Navigate to it
* git clone git@bitbucket.org:BennieBoekWurm/treetool.git
* Now you can import it from your project folders as import subfolder.treetool.treetool import AllpartsJson
* Note that the above is depended on a treetool.txt file that exists in folder C:\PTC\Bar_Start_Creo\drawing-exchange
* You can generate the treetool.txt file manually by typing treetool01 when you have an active assembly open in CREO.
* If you have CREOSON and CREO you can generate the treetool.txt file by setting get_creo to True AllpartsJson(get_creo=True)
* You can also specify the exact parameters to pull by using the two dimentional array list
* example: [["Note", "First Line"],["Info","Feat ID"],["Info","Feat #"],["Model Params","ITEMCODE"]]
* You can deeper understand the options by refering to C:\PTC\creo_stds\tree_config\analysis.cfg



### Who do I talk to? ###

* Martin Cronje (Product Owner/Contributor) - <martin.cronje@barrowsglobal.com>
* Hein Gericke (Contributor) - <hein.gericke@barrowsglobal.com>
* Michael Caloba (Contributor) - <michael.caloba@barrowsglobal.com>

---

#### NOTICE: This is a Barrows Global (https://www.barrowsglobal.com/) software product