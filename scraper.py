import code
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
from itertools import zip_longest
from io import StringIO
import copy

departments = [
    ("ASIA", "ASIAN+STUDIES"),
    ("ASIA", "ASIAN+STUDIES+WITH+THESIS"),
    ("ATA", "ATATURK+INSTITUTE+FOR+MODERN+TURKISH+HISTORY"),
    ("BM", "BIOMEDICAL+ENGINEERING"),
    ("BIS", "BUSINESS+INFORMATION+SYSTEMS"),
    ("BIS", "BUSINESS+INFORMATION+SYSTEMS+(WITH+THESIS)"),
    ("CHE", "CHEMICAL+ENGINEERING"),
    ("CHEM", "CHEMISTRY"),
    ("CE", "CIVIL+ENGINEERING"),
    ("COGS", "COGNITIVE+SCIENCE"),
    ("CSE", "COMPUTATIONAL+SCIENCE+%26+ENGINEERING"),
    ("CET", "COMPUTER+EDUCATION+%26+EDUCATIONAL+TECHNOLOGY"),
    ("CMPE", "COMPUTER+ENGINEERING"),
    ("CEM", "CONSTRUCTION+ENGINEERING+AND+MANAGEMENT"),
    ("CCS", "CRITICAL+AND+CULTURAL+STUDIES"),
    ("DSAI", "DATA+SCIENCE+AND+ARTIFICIAL+INTELLIGENCE"),
    ("PRED", "EARLY+CHILDHOOD+EDUCATION"),
    ("EQE", "EARTHQUAKE+ENGINEERING"),
    ("EC", "ECONOMICS"),
    ("EF", "ECONOMICS+AND+FINANCE"),
    ("ED", "EDUCATIONAL+SCIENCES"),
    ("CET", "EDUCATIONAL+TECHNOLOGY"),
    ("EE", "ELECTRICAL+%26+ELECTRONICS+ENGINEERING"),
    ("ETM", "ENGINEERING+AND+TECHNOLOGY+MANAGEMENT"),
    ("LL", "ENGLISH+LITERATURE"),
    ("ENV", "ENVIRONMENTAL+SCIENCES"),
    ("ENVT", "ENVIRONMENTAL+TECHNOLOGY"),
    ("XMBA", "EXECUTIVE+MBA"),
    ("FE", "FINANCIAL+ENGINEERING"),
    ("PA", "FINE+ARTS"),
    ("FLED", "FOREIGN+LANGUAGE+EDUCATION"),
    ("GED", "GEODESY"),
    ("GPH", "GEOPHYSICS"),
    ("GUID", "GUIDANCE+%26+PSYCHOLOGICAL+COUNSELING"),
    ("HIST", "HISTORY"),
    ("HUM", "HUMANITIES+COURSES+COORDINATOR"),
    ("IE", "INDUSTRIAL+ENGINEERING"),
    ("MIR", r"INTERNATIONAL+RELATIONS%3aTURKEY%2cEUROPE+AND+THE+MIDDLE+EAST"),
    ("MIR", r"INTERNATIONAL+RELATIONS%3aTURKEY%2cEUROPE+AND+THE+MIDDLE+EAST+WITH+THESIS"),
    ("INTT", "INTERNATIONAL+TRADE"),
    ("INTT", "INTERNATIONAL+TRADE+MANAGEMENT"),
    ("LAW", "LAW+PR."),
    ("LS", "LEARNING+SCIENCES"),
    ("LING", "LINGUISTICS"),
    ("AD", "MANAGEMENT"),
    ("MIS", "MANAGEMENT+INFORMATION+SYSTEMS"),
    ("MATH", "MATHEMATICS"),
    ("SCED", "MATHEMATICS+AND+SCIENCE+EDUCATION"),
    ("ME", "MECHANICAL+ENGINEERING"),
    ("MECA", "MECHATRONICS+ENGINEERING+(WITH+THESIS)"),
    ("MECA", "MECHATRONICS+ENGINEERING+(WITHOUT+THESIS)"),
    ("BIO", "MOLECULAR+BIOLOGY+%26+GENETICS"),
    ("PF", "PEDAGOGICAL+FORMATION+CERTIFICATE+PROGRAM"),
    ("PHIL", "PHILOSOPHY"),
    ("PE", "PHYSICAL+EDUCATION"),
    ("PHYS", "PHYSICS"),
    ("POLS", "POLITICAL+SCIENCE%26INTERNATIONAL+RELATIONS"),
    ("PSY", "PSYCHOLOGY"),
    ("YADYOK", "SCHOOL+OF+FOREIGN+LANGUAGES"),
    ("SPL", "SOCIAL+POLICY+WITH+THESIS"),
    ("SOC", "SOCIOLOGY"),
    ("SWE", "SOFTWARE+ENGINEERING"),
    ("SWE", "SOFTWARE+ENGINEERING+WITH+THESIS"),
    ("TRM", "SUSTAINABLE+TOURISM+MANAGEMENT"),
    ("SCO", "SYSTEMS+%26+CONTROL+ENGINEERING"),
    ("TRM", "TOURISM+ADMINISTRATION"),
    ("TRM", "TOURISM+MANAGEMENT"),
    ("WTR", "TRANSLATION"),
    ("TR", "TRANSLATION+AND+INTERPRETING+STUDIES"),
    ("TK", "TURKISH+COURSES+COORDINATOR"),
    ("TKL", "TURKISH+LANGUAGE+%26+LITERATURE"),
    ("PRSO", "UNDERGRADUATE+PROGRAM+IN+PRESCHOOL+EDUCATION"),
    ("LL", "WESTERN+LANGUAGES+%26+LITERATURES")
]

link_template = "https://registration.bogazici.edu.tr/scripts/sch.asp?donem={semester}&kisaadi={shortname}&bolum={department}"

def get_valid_choice(max_choice, prompt):
    choice = 0
    while choice < 1 or choice > max_choice:
        try:
            choice = int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")
            choice = 0
    return choice

# choose a department
dept_options = [d[0] for d in departments]
dept = "CMPE"
if globals().get("dept") is None or dept not in dept_options:
    print("Choose a department:")
    for i, d in enumerate(dept_options):
        print(f"{i+1}. {d}")

    # ask the user to choose one until a valid choice is made
    choice = get_valid_choice(len(dept_options), "Enter the number of the department short-name: ")
    dept = dept_options[choice-1]

# determine the department
department_options = [d for d in departments if d[0] == dept]
if len(department_options) == 0:
    raise ValueError("Department not found")
if len(department_options) > 1:
    # ask the user to choose one
    print("Choose a department:")
    for i, (shortname, department) in enumerate(department_options):
        print(f"{i+1}. {department}")
    choice = get_valid_choice(len(department_options), "Enter the number of the department long-name: ")
    department = department_options[choice-1][1]
else:
    department = department_options[0][1]

semester = "2024/2025-1"

# prepare the link for the department
link = link_template.format(semester=semester, shortname=dept, department=department)

# visit link with beautifulsoup
# the site has encoding "iso8859-9"
response = requests.get(link)
response.encoding = "iso8859-9"
soup = BeautifulSoup(response.text, "html.parser")

# find the tr with class name schtitle
schtitle = soup.find("tr", class_="schtitle")
if not isinstance(schtitle, Tag):
    raise ValueError("schtitle not found")

# reach to the table of schtitle
table = schtitle
while table.name != "table" and table.parent is not None:
    table = table.parent

# convert the table into dataframe
ds = pd.read_html(StringIO(str(table)), header=0, converters={'Hours': str})[0]
ds["Code.Sec"] = ds["Code.Sec"].ffill()

# stringify the days and hours with one character to indicate the day/hour for each slot
ds["Days"] = ds["Days"].str.replace("Th", "H").fillna("")
ds["Hours"] = ds["Hours"].str.replace("1112", "BC").str.replace("1011", "AB").str.replace("10", "A").fillna("")

# split the rooms by the separator " | "
ds["Rooms"] = ds["Rooms"].str.split(" | ", regex=False)

# we are sure that days and hours have the same length
# rooms can be unset, in which case we should fill it with empty strings
rooms_unset_mask = ds["Rooms"].isna()
ds.loc[rooms_unset_mask, "Rooms"] = ds.loc[rooms_unset_mask, "Days"].apply(lambda x: [""] * len(x))

# split the days and hours into lists
ds["Days"] = ds["Days"].str.split("(?<=.)(?=.)")
ds["Hours"] = ds["Hours"].str.split("(?<=.)(?=.)")

# create a new column for slots
# ds["Slots"] = ds.apply(lambda row: list(zip_longest(row["Rooms"], row["Days"], row["Hours"], fillvalue="")), axis=1)

# explode ds on rooms, days, hours, and slots
ds = ds.explode(["Rooms", "Days", "Hours"])

# rooms become NaN for whatever reason, so we need to fill them with empty strings
ds["Rooms"] = ds["Rooms"].fillna("")

# prepare a label column that is the Code.Sec + a space + the initials of the Instr.
ds["Label"] = ds["Code.Sec"] + " " + ds["Instr."].str.replace(r"(?<=\w).", "", regex=True)

# take out the rows that have their Days&Hours as blank into a separate dataframe
ds_no_days_hours = ds[(ds["Days"] == "") & (ds["Hours"] == "")]
ds = ds[(ds["Days"] != "") | (ds["Hours"] != "")]

# pivot the table to have rooms as rows, days as subrows, and hours as columns
ds = ds.pivot_table(index=["Rooms", "Days"], columns="Hours", values="Label", dropna=False, aggfunc=lambda x: "\n".join(x))

# sort days
ds = ds.reindex(["", "M", "T", "W", "H", "F"], level=1)

# replace days with their full names
# replace hours with their full names and labels
ds = ds.rename(
    index={"M": "Monday", "T": "Tuesday", "W": "Wednesday", "H": "Thursday", "F": "Friday"},
    columns={"A": "10\n18:00-18:50", "1": "1\n09:00-09:50", "2": "2\n10:00-10:50", "3": "3\n11:00-11:50", "4": "4\n12:00-12:50", "5": "5\n13:00-13:50", "6": "6\n14:00-14:50", "7": "7\n15:00-15:50", "8": "8\n16:00-16:50", "9": "9\n17:00-17:50"})

years, term = semester.split("-")
year1, year2 = years.split("/")
# semester_friendly_name = f"{year1}_{year2}_{term}"
# filename = f"{dept}_{semester_friendly_name}.xlsx"
semester_friendly_name = f"{year1} Fall" if term == "1" else f"{year2} Spring" if term == "2" else f"{year2} Summer"
filename = f"{dept} {semester_friendly_name}.xlsx"

# save this to an excel file with a sheet for each room
with pd.ExcelWriter(filename) as writer:
    def format_worksheet(worksheet, num_columns, column_width):
        for col in map(chr, range(ord("A"), ord("A") + num_columns)):
            worksheet.column_dimensions[col].width = column_width

        # turn on text wrapping and center alignment (vertical and horizontal)
        # partially thanks to: https://stackoverflow.com/a/63140906/2736228
        for row in worksheet.iter_rows():
            for cell in row:
                alignment = copy.copy(cell.alignment)
                alignment.wrapText = True
                alignment.vertical = "center"
                alignment.horizontal = "center"
                cell.alignment = alignment
    
    # save the no days hours dataframe to a sheet named "No Days Hours"
    ds_no_days_hours["Label"].rename("Courses without time").to_excel(writer, sheet_name="No Time", index=False)
    format_worksheet(writer.sheets["No Time"], 1, 20)

    for room in ds.index.get_level_values("Rooms").unique():
        roomlabel = room if room else "No Room"
        ds.loc[room].to_excel(writer, sheet_name=roomlabel)

        # set column widths to fit the content
        format_worksheet(writer.sheets[roomlabel], ds.shape[1]+1, 16)

# code.interact(local=locals())

