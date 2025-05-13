let bucket = [];

function saveBucketAndGoToOrderDetails() {
  fetch("/save_bucket", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ bucket }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        window.location.href = "/order_details";
      } else {
        alert("Failed to save bucket!");
      }
    });
}

function updateBucketDisplay() {
  const iconCount = document.getElementById("bucket-count-icon");
  const summary = document.getElementById("bucket-summary");
  if (!iconCount || !summary) return;

  const totalItems = bucket.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = bucket.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  iconCount.textContent = totalItems;
  summary.textContent = `Subtotal: Rs. ${totalPrice}`;
}

function attachMenuButtons() {
  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.dataset.id);
      const action = btn.dataset.action;
      const name = btn.dataset.name;
      const price = parseFloat(btn.dataset.price);
      let qtyEl = document.getElementById(`qty-${id}`);
      let quantity = parseInt(qtyEl?.textContent || "1");

      let item = bucket.find((i) => i.id === id);

      if (action === "increase") {
        quantity = Math.min(99, quantity + 1);
        qtyEl.textContent = quantity;
      } else if (action === "decrease") {
        quantity = Math.max(1, quantity - 1);
        qtyEl.textContent = quantity;
      } else if (action === "add") {
        if (item) {
          item.quantity += quantity;
        } else {
          bucket.push({ id, name, price, quantity });
        }
        qtyEl.textContent = 1; // Reset
        updateBucketDisplay();
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("menu-list")) {
    const restaurantId = document.getElementById("restaurantId").value;
    fetch(`/api/menu?restaurant_id=${restaurantId}`)
      .then((response) => response.json())
      .then((data) => {
        const menuContainer = document.getElementById("menu-list");
        const navbar = document.getElementById("category-navbar");
        const categories = Object.entries(data);

        categories.forEach(([category, items], idx) => {
          const section = createCategorySection(category, items);
          menuContainer.appendChild(section);

          navbar.appendChild(createCategoryButton(category, section));
        });

        attachMenuButtons();
        updateBucketDisplay();
      })
      .catch((err) => console.error("Menu fetch error:", err));
  }
});

function createCategorySection(category, items) {
  const section = document.createElement("section");
  section.id = category.replace(/\s+/g, "-").toLowerCase();

  const heading = document.createElement("h2");
  heading.className = "mb-2";
  heading.style.fontSize = "2.5rem";
  heading.style.fontWeight = "900";
  heading.style.textTransform = "uppercase";
  heading.style.color = "black";
  heading.textContent = category;

  // Red divider
  const divider = document.createElement("div");
  divider.style.width = "140px";
  divider.style.height = "6px";
  divider.style.background = "#E4002B";
  divider.style.borderRadius = "2px";
  divider.style.marginTop = "10px";
  divider.style.marginBottom = "24px";

  const grid = document.createElement("div");
  grid.className = "grid gap-6"; // Tailwind gap for consistent spacing
  grid.style.gridTemplateColumns = "repeat(auto-fill, minmax(220px, 1fr))";
  grid.style.justifyItems = "start"; // Align cards to the left

  items.forEach((item) => grid.appendChild(createMenuCard(item)));

  section.appendChild(heading);
  section.appendChild(divider);
  section.appendChild(grid);
  return section;
}

function createCategoryButton(category, section) {
  const btn = document.createElement("button");
  btn.textContent = category;

  // Add custom styling for black outline and KFC red hover with white text
  btn.className = "btn btn-sm";
  btn.style.border = "1px solid black";
  btn.style.backgroundColor = "transparent";
  btn.style.color = "black";
  btn.style.transition = "all 0.3s ease";

  // KFC red color on hover with white text
  btn.onmouseover = () => {
    btn.style.backgroundColor = "#E4002B"; // KFC red color
    btn.style.color = "white";
    btn.style.borderColor = "#E4002B";
  };

  // Return to outline style on mouseout
  btn.onmouseout = () => {
    btn.style.backgroundColor = "transparent";
    btn.style.color = "black";
    btn.style.borderColor = "black";
  };

  btn.onclick = () => section.scrollIntoView({ behavior: "smooth" });
  return btn;
}

function createMenuCard(item) {
  const card = document.createElement("div");
  card.className =
    "bg-white shadow rounded-lg overflow-hidden flex flex-col w-full max-w-xs";

  // Create card HTML structure
  card.innerHTML = `
  <!-- Image Container -->
  <div class="h-40 bg-gray-100 flex justify-center items-center">
    <img src="${
      item.image_url || "https://via.placeholder.com/300x200?text=No+Image"
    }"
         alt="${item.name}"
         class="object-contain max-h-32 w-auto" />
  </div>
  <!-- Content -->
  <div class="bg-gray-100 p-4 flex flex-col h-full">
    <div class="flex flex-col items-center flex-grow">
      <h2 class="text-lg font-semibold text-center">${item.name}</h2>
      <p class="text-sm text-gray-600 text-center mt-1">${
        item.description || ""
      }</p>
      <p class="font-bold text-red-600 mt-2">Rs. ${item.price}</p>
      <div class="flex items-center gap-2 mt-3">
        <button class="quantity-btn" data-id="${
          item.id
        }" data-action="decrease">−</button>
        <span id="qty-${item.id}" class="w-4 text-center">1</span>
        <button class="quantity-btn" data-id="${
          item.id
        }" data-action="increase">+</button>
      </div>
    </div>
    <button
      class="btn btn-sm w-full text-white mt-auto"
      style="background-color: #E4002B;"
      data-id="${item.id}"
      data-name="${item.name}"
      data-price="${item.price}"
      data-action="add">
      Add to Bucket
    </button>
  </div>
  `;

  // After card is created, apply custom styles to the quantity buttons
  setTimeout(() => {
    const quantityButtons = card.querySelectorAll(".quantity-btn");
    quantityButtons.forEach((btn) => {
      // Apply default styling
      btn.style.border = "1px solid black";
      btn.style.backgroundColor = "transparent";
      btn.style.color = "black";
      btn.style.borderRadius = "0.375rem";
      btn.style.padding = "0 0.5rem";
      btn.style.fontSize = "0.875rem";
      btn.style.lineHeight = "1.5rem";
      btn.style.transition = "all 0.3s ease";
      btn.style.cursor = "pointer";

      // Add hover effects
      btn.addEventListener("mouseover", () => {
        btn.style.backgroundColor = "#000000"; // KFC red
        btn.style.color = "white";
        btn.style.borderColor = "#000000";
      });

      // Return to default on mouseout
      btn.addEventListener("mouseout", () => {
        btn.style.backgroundColor = "transparent";
        btn.style.color = "black";
        btn.style.borderColor = "black";
      });
    });
  }, 0);

  return card;
}

function saveBucketAndGoToOrderDetails() {
  alert("Button clicked!");
  fetch("/save_bucket", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ bucket }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        window.location.href = "/order_details";
      } else {
        alert("Failed to save bucket!");
      }
    });
}
