<script setup>
import { ref, reactive } from 'vue'
import { onMounted } from 'vue';

function getQueryParam(name) {
  const url = new URL(window.location.href)
  return url.searchParams.get(name)
}

const userId = ref(getQueryParam('user_id') || 1)
const profitPerTap = ref(1)
const profitPerHour = ref(0)

const notification = ref('')

const showUpgradeOverlay = ref(false)
const selectedCard = ref(null)

const upgradeInfo = reactive({
    name: '',
    description: '',
    image: '',
    cost: 0,
    level: 0,
})

const cardManualData = {
    token: { name: 'Token', description: 'Increases the amount of coins you receive per hour', image: 'token.png' },
    staking: { name: 'Staking', description: 'Increases the amount of coins you receive per hour', image: 'staking.png' },
    genesis: { name: 'Genesis', description: 'Increases the amount of coins you receive per hour', image: 'genesis.png' },
    echeleon: { name: 'Echeleon', description: 'Increases the amount of coins you receive per hour', image: 'echeleon.png' },
    ledger: { name: 'Ledger', description: 'Increases the amount of coins you receive per hour', image: 'ledger.png' },
    quantum: { name: 'Quantum', description: 'Increases the amount of coins you receive per hour', image: 'quantum.png' },
    multitap: { name: 'Multitap', description: 'Increases the amount of coins you can get in one touch', image: 'click.png' },
}

function recalcProfits(cardsArr) {
  const multitapCard = cardsArr.find(c => c.type === 'multitap')
  profitPerTap.value = multitapCard ? multitapCard.profit : 1

  profitPerHour.value = cardsArr
    .filter(c => c.type !== 'multitap')
    .reduce((sum, c) => sum + (c.profit || 0), 0)
}

async function showUpgradeBlock(cardType) {
  try {
    const res = await fetch(`/get_card_data?user_id=${userId.value}&card_type=${cardType}`)
    if (!res.ok) throw new Error('Failed to fetch card data')

    const data = await res.json()
    const manual = cardManualData[cardType]

    upgradeInfo.name = manual.name
    upgradeInfo.description = manual.description
    upgradeInfo.image = `src/assets/${manual.image}`
    upgradeInfo.cost = data.cost
    upgradeInfo.level = data.level + 1

    selectedCard.value = cardType
    showUpgradeOverlay.value = true
    document.body.style.overflow = 'hidden'
  } catch (e) {
    console.error(e)
  }
}

async function upgradeCard() {
  if (!selectedCard.value) return;

  try {
    const res = await fetch('/upgrade_card', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId.value, card_type: selectedCard.value }),
    });

    showUpgradeOverlay.value = false;
    document.body.style.overflow = 'auto';

    if (res.ok) {
      notification.value = 'success';
      await fetchUserCards();
      setTimeout(() => (notification.value = ''), 1500);
    } else {
      notification.value = 'fail';
      setTimeout(() => (notification.value = ''), 1500);
    }
  } catch (e) {
    console.error('Upgrade failed:', e);
    notification.value = 'fail';
    setTimeout(() => (notification.value = ''), 1500);
  }
}

function closeUpgrade() {
  showUpgradeOverlay.value = false
  document.body.style.overflow = 'scroll'
}
const cards = ref([]);

async function fetchUserCards() {
  try {
    const res = await fetch(`/get_user_cards?user_id=${userId.value}`);
    if (!res.ok) throw new Error('Failed to fetch user cards');
    const userCards = await res.json();
    cards.value = userCards.map(card => ({
      ...card,
      title: cardManualData[card.type]?.name || card.type,
      description: cardManualData[card.type]?.description || '',
      image: cardManualData[card.type]?.image || '',
    }));
    recalcProfits(cards.value);
  } catch (e) {
    console.error(e);
  }
}
onMounted(() => {
  fetchUserCards();
});
</script>

<template>
  <div class="container">
    <h1>Market</h1>

    <div id="copy-notification" v-if="notification === 'success'">Card upgrade!</div>
    <div id="copy-notification-false" v-if="notification === 'fail'">Not enough money!</div>


    <div class="hour" id="block_hour">
      <div
        v-for="card in cards"
        :key="card.type"
        :id="`${card.type}-card`"
        :class="['card', card.type === 'multitap' ? 'multitap' : '']"
      >
        <div v-if="card.type !== 'multitap'" class="card-icons">
          <img :src="`src/assets/${card.type}.png`" :alt="card.type" />
          <div class="card-content">
            <div class="card-title">{{ card.title }}</div>
            <div class="card-profit">Profit per hour</div>
            <div class="profit-value">
              <img src="src/assets/coin.png" alt="Coin" class="coin-icon-profit" />
              <p>+{{ card.profit }}</p>
            </div>
          </div>
        </div>

        <div v-else class="multitap-icons">
          <img src="src/assets/click.png" alt="Multitap" />
          <div class="card-content">
            <div class="card-title-multitap">Multitap</div>
            <div class="profit-value-multitap">
              <img src="src/assets/coin.png" alt="Coin" id="multitap-coin-icon-profit" />
              <p>{{ card.cost }}</p>
              <span>lvl {{ card.level }}</span>
            </div>
          </div>
        </div>

        <div class="card-footer" v-if="card.type !== 'multitap'">
          <span>lvl {{ card.level }}</span>
          <span>{{ card.cost }}</span>
        </div>

        <div class="botton-border" v-if="card.type === 'multitap'"></div>
        <button class="upgrade" v-if="card.level < 20" @click="showUpgradeBlock(card.type)">Upgrade</button>
        <div v-else class="upgrade-max-level" style="color:#fbc02d; margin-top:10px; font-weight:bold;">Maximum level</div>
      </div>
    </div>

    <div class="upgrade-overlay" v-show="showUpgradeOverlay" @click="closeUpgrade"></div>
    <transition name="fade-up">
        <div class="upgrade-block" v-if="showUpgradeOverlay">
            <div class="upgrade-top">
            <img :src="upgradeInfo.image" class="upgrade-image" />
            </div>
            <h1>{{ upgradeInfo.name }}</h1>
            <p class="upgrade-description">{{ upgradeInfo.description }}</p>
            <div class="upgrade-footer">
            <img src="src/assets/coin.png" alt="Coin" />
            <p class="upgrade-cost">{{ upgradeInfo.cost }}</p>
            <p class="upgrade-level">● {{ upgradeInfo.level }} lvl</p>
            </div>
            <button class="upgrade-action" @click="upgradeCard">Upgrade</button>
        </div>
    </transition>
    </div>
</template>

<style scoped>
h1 {
    margin-top: 3%;
    margin-bottom: 3%;
    font-size: 1.6em;
}

.container {
    display: block;
    margin: 0 auto;
    justify-content: center;
    align-items: center;
    height: 78%;
    background: #1e1e1e;
    border-radius: 30px 30px 30px 30px;
    padding: 20px;
    padding-left: 0%;
    padding-right: 0%;
    box-shadow: 0px 0px 8px #6366F1;
    text-align: center;
    overflow-y: auto;
    overflow-x: hidden;
}

.sections-button {
    flex: 1;
    margin: 0 20px;
    text-decoration: none;    
    color: #ffffff;
    padding: 10px 10px;    
    background: #292929;
    border-radius: 8px;   
    border: none; 
    transition: background-color 0.3s;
    text-align: center;    
    font-size: 1.1em;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
}

.sections-button:hover {
    background-color: #383838;    
    text-decoration: none;
}

.sections-button:active {    
    outline: none;
    background-color: #535454;
    color: #ffffff;
}

.sections-button:focus {    
    outline: none; 
    background-color: #444444;   
    color: #ffffff; 
}

.tap {
    display: none;
}

.hour {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2%; 
    margin-top: 5%;
    margin-bottom: 20%;
}

.card {
    width: 40%;
    background: #292929;
    padding: 15px;
    border-radius: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    text-align: center;
    color: white;
    font-family: Arial, sans-serif;
    margin-bottom: 20px;
}

.card-icons {
    display: flex;
    align-items: center;
    margin-bottom: 5%;
}

.card-icons img {
    width: 35%;
    height: 35%;
}

.card-content {
    flex: 1;
    text-align: left;
    padding-left: 5%;
}

.card-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 5px;
}

.card-profit {
    color: #bbb;
    font-size: 12px;
    font-weight: bold;
}

.profit-value {
    font-size: 20px;
    font-weight: bold;
    color: #fbc02d;
    display: flex;
    align-items: center;
    margin-top: 8%;
}

.profit-value p{
    margin: 0;
    margin-top: 2%;
}

#coin-icon-profit {
    width: 25%;
    height: 25%;
    margin-right: 5px;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    padding-top: 2%;
    font-size: 14px;
    color: #bbb;
    border-top: 2px dashed rgb(56, 56, 56);
}


.multitap {
    width: 80%;
    background: #292929;
    padding: 10px;
    border-radius: 25px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    text-align: center;
    color: white;
    font-family: Arial, sans-serif;
    margin-bottom: 10px;
}

.multitap-icons {
    display: flex;
    align-items: center;
    margin-bottom: 2%;
}

.multitap-icons img {
    width: 25%;
    height: 20%;
}

#multitap-coin-icon-profit {
    width: 15%;
    height: 15%;
    margin-right: 5px;
}

.profit-value-multitap {
    font-size: 20px;
    color: #fbc02d;
    display: flex;
    align-items: center;
}

.profit-value-multitap span{
    color: #bbb;
    margin-left: 10%;
}

.card-title-multitap {
    font-size: 18px;
    margin-left: 20%;
}

@media (max-width: 385px) {
    .card-icons img {
        width: 30%;
        height: 30%;
    }
    
    .card-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .card-profit {
        font-size: 12px;
    }
    
    .profit-value {
        font-size: 20px;
    }
    
}

@media (max-width: 355px) {
    .card-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .card-profit {
        font-size: 11px;
    }
    
    .profit-value {
        font-size: 18px;
    }
    .sections-button {
        margin: 0 20px;
        padding: 10px 10px;     
        font-size: 1.0em;
    }
    
}

.card button {
    background-color: #292929;
    color: white;
    border: 1px solid black;
    padding: 10px;
    border-radius: 50px;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent; 
}

.card button:hover {
    background-color: #383838;
}

#copy-notification {
    display: block;
    position: fixed;
    bottom: 90%;
    left: 50%;
    transform: translateX(-50%);
    background-color: #333333de;
    color: rgb(9, 158, 34);
    padding: 10px;
    border: 2px solid black;
    border-radius: 15px;
    z-index: 1000;
    transition: all 0.5s;
}

#copy-notification-false {
    display: block;
    position: fixed;
    bottom: 90%;
    left: 50%;
    transform: translateX(-50%);
    background-color: #333333de;
    color: rgb(179, 6, 6);
    padding: 10px;
    border: 2px solid black;
    border-radius: 15px;
    z-index: 1000;
    transition: all 0.3s;
}

.upgrade-overlay {
    display: block;
    position: fixed;
    z-index: 9;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(5px);

}


.upgrade-block {
    padding-top: 1%;
    position: fixed;
    bottom: 0;  
    display: flex;
    top:40%;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
    height: 50%;
    border: none;
    border-top: 1px solid #6366F1;
    border-radius: 30px 30px 0px 0px;
    background-color: #292929;
    z-index: 10;
    transition: all 1s;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.upgrade-block button{
    width: 80%;
    height: 18%;
    border: none;
    border-radius: 30px;
    margin: 2%;
    background-color:#773ffa8f;
    font-size: 20px;
    color: white;
    align-items: center;
    justify-content: center;
    text-align: center;
    -webkit-tap-highlight-color: transparent; 
    box-shadow: 0px 3px 8px #6366F1;
}

.upgrade-block p {
    font-size: 20px;
    margin: 1%;

}




.fade-up-enter-active, .fade-up-leave-active {
  transition: all 1s ;
}
.fade-up-enter-from,
.fade-up-leave-to {
  top: 100%;
}
.fade-up-enter-to, .fade-up-leave-from {
    top: 40%;
}



.upgrade-block button:hover{
    background-color: #1f1f1f;

}
.upgrade-block button:focus{
    background-color: #1f1f1f;


}

.upgrade-description {
    width: 80%;
}



#upgrade-cost {
    font-weight: bold;
    font-size: 26px;
    margin-left: 2%;
}

#upgrade-level{
    font-weight: bold;
    color: rgb(97, 97, 97);
    font-size: 26px;
}
.upgrade-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 4%;
    margin-bottom: 4%;
}

.upgrade-footer p{
    margin: 0;
    padding: 0;
    margin-left: 5%;
}

.upgrade-footer img{
    width: 15%;
    height: auto;
}

.upgrade-top {
    display: flex;
    justify-content: center; 
    align-items: center;
    position: relative; 
    width: 100%;
    
}



.upgrade-image {
    width: 20%;
    height: auto;
}


.multitap button {
    width: 80%;
    background-color: #292929;
    color: white;
    border: 1px solid black;
    padding: 10px;
    border-radius: 50px;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent; 
}

.botton-border{
    border-top: 2px dashed rgb(56, 56, 56);
    margin-bottom: 3%;
}
</style>
