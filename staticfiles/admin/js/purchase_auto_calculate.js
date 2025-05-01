document.addEventListener("DOMContentLoaded", function () {
  // Recalculate cost per package and cost per item dynamically
  function recalculate() {
    let boxQty =
      parseFloat(document.getElementById("id_box_quantity")?.value) || 0;
    let packagesPerBox =
      parseFloat(document.getElementById("id_packages_per_box")?.value) || 0;
    let itemsPerPackage =
      parseFloat(document.getElementById("id_items_per_package")?.value) || 0;

    let costPerBoxField = document.getElementById("id_cost_per_box");
    let costPerPackageField = document.getElementById("id_cost_per_package");
    let costPerItemField = document.getElementById("id_cost_per_item");

    let costPerBox = parseFloat(costPerBoxField?.value) || 0;
    let costPerPackage = parseFloat(costPerPackageField?.value) || 0;
    let costPerItem = parseFloat(costPerItemField?.value) || 0;

    // If cost per box and packages per box are provided, calculate cost per package
    if (costPerBox > 0 && packagesPerBox > 0) {
      let calculatedPackageCost = costPerBox / packagesPerBox;
      costPerPackageField.value = calculatedPackageCost.toFixed(2);

      // If items per package are provided, calculate cost per item
      if (itemsPerPackage > 0) {
        let calculatedItemCost = calculatedPackageCost / itemsPerPackage;
        costPerItemField.value = calculatedItemCost.toFixed(2);
      }
    } else if (costPerPackage > 0 && itemsPerPackage > 0) {
      // If cost per package is provided and items per package are provided, calculate cost per item
      let calculatedItemCost = costPerPackage / itemsPerPackage;
      costPerItemField.value = calculatedItemCost.toFixed(2);
    }
  }

  // Calculate total cost based on the entered values
  function calculateTotalCost() {
    const boxQuantity =
      parseFloat(document.getElementById("id_box_quantity")?.value) || 0;
    const packagesPerBox =
      parseFloat(document.getElementById("id_packages_per_box")?.value) || 0;
    const itemsPerPackage =
      parseFloat(document.getElementById("id_items_per_package")?.value) || 0;

    const costPerBox =
      parseFloat(document.getElementById("id_cost_per_box")?.value) || 0;
    const costPerPackage =
      parseFloat(document.getElementById("id_cost_per_package")?.value) || 0;
    const costPerItem =
      parseFloat(document.getElementById("id_cost_per_item")?.value) || 0;

    let totalCost = 0;

    // Calculate total cost based on the available data
    if (boxQuantity > 0 && costPerBox > 0) {
      totalCost = boxQuantity * costPerBox;
    } else if (boxQuantity > 0 && packagesPerBox > 0 && costPerPackage > 0) {
      totalCost = boxQuantity * packagesPerBox * costPerPackage;
    } else if (
      boxQuantity > 0 &&
      packagesPerBox > 0 &&
      itemsPerPackage > 0 &&
      costPerItem > 0
    ) {
      totalCost = boxQuantity * packagesPerBox * itemsPerPackage * costPerItem;
    } else if (packagesPerBox > 0 && costPerPackage > 0) {
      totalCost = packagesPerBox * costPerPackage;
    } else if (itemsPerPackage > 0 && costPerItem > 0) {
      totalCost = itemsPerPackage * costPerItem;
    }

    // Update the total cost value in the form
    const totalCostField = document.getElementById("id_total_cost_value");
    if (totalCostField) {
      totalCostField.value = totalCost.toFixed(2);
    }
  }

  // Add event listeners to all relevant input fields to trigger recalculation
  [
    "id_box_quantity",
    "id_packages_per_box",
    "id_items_per_package",
    "id_cost_per_box",
    "id_cost_per_package",
    "id_cost_per_item",
  ].forEach(function (fieldId) {
    const field = document.getElementById(fieldId);
    if (field) {
      field.addEventListener("input", function () {
        recalculate();
        calculateTotalCost();
      });
    }
  });
});
