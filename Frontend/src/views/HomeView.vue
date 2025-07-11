<script setup>
    import { ref, computed, onMounted } from 'vue'
    
    function getQueryParam(name) {
      const url = new URL(window.location.href)
      return url.searchParams.get(name)
    }
    const username = ref(getQueryParam('username') || 'User')
    const userId = ref(getQueryParam('user_id') || 1)

    const coins = ref(0)
    const profitPerTap = ref(1)
    const profitPerHour = ref(0)
    const level = ref(1)
    const progress = ref(0)
    const nextLevelCoins = ref(5000)
    const nextLevelCoinsText = ref('5000')
    const showPopup = ref(false)
    const profitMessage = ref('')
    const plusOnes = ref([])

    const levelThresholds = [
      0, 5000, 25000, 100000, 1000000, 2000000, 10000000, 50000000, 1000000000, 10000000000
    ]

    function calculateLevel(score) {
      for (let i = levelThresholds.length - 1; i >= 0; i--) {
          if (score >= levelThresholds[i]) {
          return i + 1
          }
      }
      return 1
    }

    function calculateProgress(score, curLevel) {
      const currentLevelThreshold = levelThresholds[curLevel - 1]
      const nextLevelThreshold = levelThresholds[curLevel] || currentLevelThreshold
      const prog = ((score - currentLevelThreshold) / (nextLevelThreshold - currentLevelThreshold)) * 100
      return Math.min(Math.max(prog, 0), 100)
    }

    function calculateCoinsToNextLevel(score, curLevel) {
      if (curLevel >= levelThresholds.length) return "Max level"
      const nextLevelThreshold = levelThresholds[curLevel]
      return nextLevelThreshold > 0 ? nextLevelThreshold : 0
    }

    function updateLevelProgressAndCoins() {
      const newLevel = calculateLevel(coins.value)
      if (newLevel > level.value) {
          level.value = newLevel
      }
      if (level.value >= levelThresholds.length) {
          progress.value = 100
          nextLevelCoinsText.value = "Max level"
      } else {
          progress.value = calculateProgress(coins.value, level.value)
          nextLevelCoinsText.value = calculateCoinsToNextLevel(coins.value, level.value)
      }
    }

    function showProfitPopup(amount) {
      if (amount && amount > 0) {
          profitMessage.value = `While you were away, your earned ${amount} coins!`
          showPopup.value = true
      }
    }

    function closePopup() {
      showPopup.value = false
    }

  async function fetchUserData() {
    try {
      const response = await fetch(`/user_data?user_id=${userId.value}`);
      const contentType = response.headers.get('content-type') || '';
      if (!response.ok) {
        const errorText = await response.text();
        console.error("HTTP error", response.status, errorText);
        return;
      }
      if (!contentType.includes('application/json')) {
        const errorText = await response.text();
        console.error("Not JSON response!", errorText);
        return;
      }
      const data = await response.json();
      if (data.success) {
        coins.value = data.coins;
        profitPerTap.value = data.profit_per_tap;
        profitPerHour.value = data.profit_per_hour;
        updateLevelProgressAndCoins();
      showProfitPopup(data.profit_gained);
      } else {
        console.error("Server returned error:", data);
      }
    } catch (error) {
      console.error("Fetch failed:", error);
    }
  }

  async function updateCoinsOnServer() {
    try {
        const response = await fetch('/update_coins', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'User-ID': userId.value
        },
        body: JSON.stringify({ coins: coins.value })
        })
        await response.json()
    } catch (error) {}
  }
  const hamster = ref(null);
  const DEG = 40;
  function onHamsterClick(event) {
    coins.value += profitPerTap.value
    updateLevelProgressAndCoins()
    updateCoinsOnServer()

    const rect = hamster.value.getBoundingClientRect();
    const offsetX = event.clientX - rect.left - rect.width / 2;
    const offsetY = event.clientY - rect.top - rect.height / 2;

    const tiltX = (offsetY / rect.height) * DEG;
    const tiltY = (offsetX / rect.width) * -DEG;

    hamster.value.style.setProperty('--tiltX', `${tiltX}deg`);
    hamster.value.style.setProperty('--tiltY', `${tiltY}deg`);

    setTimeout(() => {
      hamster.value.style.setProperty('--tiltX', `0deg`);
      hamster.value.style.setProperty('--tiltY', `0deg`);
    }, 300);

    // Анимация +N
    const id = Date.now() + Math.random()
    plusOnes.value.push({
        id,
        x: event.clientX,
        y: event.clientY
    })
    setTimeout(() => {
        plusOnes.value = plusOnes.value.filter(plus => plus.id !== id)
    }, 1000)
  }

  onMounted(async () => {
    await fetchUserData()
  })
</script>

<template>
  <div class="container">
    <div id="username" class="header">{{ username }}</div>

    <div class="stats">
      <div class="stat">
        <div id="tap" class="stat-label">Earn per tap</div>
        <div class="stat-value">+{{ profitPerTap }}</div>
      </div>
      <div class="stat">
        <div id="up" class="stat-label">Coins to level up</div>
        <div class="stat-value" id="coins-to-up">{{ nextLevelCoinsText }}</div>
      </div>
      <div class="stat">
        <div id="hourse" class="stat-label">Profit per hour</div>
        <div class="stat-value">{{ profitPerHour }}</div>
      </div>
    </div>

    <div class="coin" id="coin">
      <img class="money" src="/src/assets/coin.png" alt="Coin">
      <span id="score">{{ coins }}</span>
    </div>

    <div class="level-bar">
      <div class="level-progress" :style="{ width: progress + '%' }"></div>
      <div class="level-text">Level {{ level }}/10</div>
    </div>

    <div id="hamster" class="hamster" @click="onHamsterClick" ref="hamster"></div>
    <div
      v-for="plus in plusOnes"
      :key="plus.id"
      class="floating-plus-one"
      :style="{ left: plus.x + 'px', top: plus.y + 'px' }"
    >+{{ profitPerTap }}</div>
  </div>

  <div class="main-overlay" :class="{ active: showPopup }"></div>
  <div id="profit-popup" class="popup" :style="{ top: showPopup ? '0' : '100%' }">
    <div class="popup-content">
      <span id="profit-message">{{ profitMessage }}</span>
      <button id="profit-close-btn" @click="closePopup">Get coins</button>
    </div>
  </div>
</template>

<style scoped>
.container {
    display:block;
    margin:0 auto;
    justify-content: center;
    align-items: center;
    height:78%;
    background: #1e1e1e;
    border-radius: 30px 30px 30px 30px;
    padding: 20px;
    box-shadow: 0px 0px 8px #6366F1;
    text-align: center;
    overflow-y: auto; /* Добавлено для вертикальной прокрутки */
    overflow-x: hidden;
}

.header {
    margin-bottom: 20px;
    font-size: 1.5em;
    font-weight: bold;
    user-select: none;
}



.stats {
    display: flex;
    justify-content: space-between;

}

.stat {
    margin:5px;
    text-align: center;
    background: #292929;
    border-radius: 10px;
    padding: 3px;
    user-select: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.stat-value {
    font-size: 1.1em;
    font-weight: bold;
    color: white;
    padding-top:5px;
}

.stat-label {
    font-size: 0.8em;
    padding-left:5px;
    padding-right:5px;
    padding-top:5px;
}
#tap{
    color:#FFA500;
}
#up{
    color:#6A5ACD;
}
#hourse{
    color:#32CD32;
}



.coin {
    display:flex;
    align-items:center;
    justify-content:center;
    font-size: 2.5em;
    font-weight: bold;
    margin: 30px 0 30px 0; /* Added top and bottom margin */
    color: white;
    user-select: none;
}
.money{
    padding-right:2%;
    width:60px;
    height:60px;
}
.level-bar {
    margin: 20px auto;
    height: 12px;
    width: 100%;
    background-color: #555;
    border-radius: 6px;
    overflow: hidden;
    position: relative;
    user-select: none;
    }

.level-progress {
    height: 100%;
    background: -webkit-linear-gradient(90deg, #6A5ACD, #00C9A7);
    background: linear-gradient(90deg, #6A5ACD, #00C9A7);
    transition: width 0.3s;
}

.level-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.9em;
    font-weight: bold;
    color: #ffffff;
}

.hamster {
    margin: 20px auto;
    margin-top:30px;
    margin-bottom:30px;
    width: 250px;
    height: 250px;
    background: url('src/assets/Mmoney.png') no-repeat center center;
    background-size: cover;
    border-radius: 50%;
    border: 5px solid #673ab7;
    transition: transform 0.2s ease;
    --tiltX: 0deg;
    --tiltY: 0deg;
    transform: rotateX(var(--tiltX)) rotateY(var(--tiltY));
}

/* Добавляем стили для анимации взлетающей цифры */
.floating-plus-one {
    position: absolute;
    font-size: 30px;
    color: #FFA500;
    animation: float 1s ease-in-out;
    user-select: none;
    pointer-events: none;
}

.main-overlay {
    display: none;
    position: fixed;
    z-index: 15;   /* Меньше, чем у .popup */
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(5px);
    transition: opacity 0.5s;
}
.main-overlay.active {
    display: block;
    opacity: 1;
}
.popup {
    display: flex;
    position: fixed;
    left: 0;
    top: 100%;
    width: 100vw;
    height: 100vh;
    z-index: 16;
    justify-content: center;
    align-items: end;
    transition: top 1s;
}

.popup-content {
    display: flex;
    flex-direction: column;
    background: #222;
    color: #fff;
    width: 100%;
    height: 45%;
    border-radius: 16px 16px 0px 0px;
    text-align: center;
    align-items: center;
    gap: 50px;
    justify-content: center;
    min-width: 220px;
}
#profit-close-btn {
    margin-top: 18px;
    padding: 25px 85px;
    font-size: 18px;
    background-color:#773ffa8f;
    color: #222;
    border: none;
    border-radius: 15px;
    cursor: pointer;
    box-shadow: 0px 3px 8px #6366F1;
}


@keyframes float {
    from {
        opacity: 1;
        transform: translateY(0);
    }
    to {
        opacity: 0;
        transform: translateY(-50px);
    }
}
</style>