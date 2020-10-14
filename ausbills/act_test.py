import io
from act_legislative_assembly import act_all_bills as all_bills

f = open("9th_assembly_demo.txt", "w")
for bill in range(len(all_bills)):
    f.write(all_bills[bill]['title'] + " - " + all_bills[bill]['date'] + "\n" + "Presented by " + all_bills[bill]['presented_by'] + "\n" + all_bills[bill]['description'] + '\n\n')