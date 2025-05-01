document.addEventListener("DOMContentLoaded", function () {
  function calculateCosts() {
    const boxQty =
      parseFloat(document.getElementById("id_box_quantity")?.value) || 0;
    const pkgPerBox =
      parseFloat(document.getElementById("id_packages_per_box")?.value) || 0;
    const itemsPerPkg =
      parseFloat(document.getElementById("id_items_per_package")?.value) || 0;
    const costPerBox =
      parseFloat(document.getElementById("id_cost_per_box")?.value) || 0;

    let costPerPackage = 0;
    let costPerItem = 0;
    let totalCost = 0;

    if (pkgPerBox > 0) {
      costPerPackage = costPerBox / pkgPerBox;
      document.getElementById("id_cost_per_package").value =
        costPerPackage.toFixed(2);
    }

    if (pkgPerBox > 0 && itemsPerPkg > 0) {
      costPerItem = costPerBox / (pkgPerBox * itemsPerPkg);
      document.getElementById("id_cost_per_item").value =
        costPerItem.toFixed(2);
    }

    totalCost = boxQty * costPerBox;
    document.getElementById("id_total_cost_value").value = totalCost.toFixed(2);
  }

  const inputs = [
    "id_box_quantity",
    "id_packages_per_box",
    "id_items_per_package",
    "id_cost_per_box",
  ];
  inputs.forEach((id) => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("input", calculateCosts);
    }
  });
});
