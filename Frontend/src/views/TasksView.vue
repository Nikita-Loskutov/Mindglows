<script setup>
    import { ref, onMounted } from 'vue'

    function getQueryParam(name) {
        const url = new URL(window.location.href)
        return url.searchParams.get(name)
    }

    const userId = ref(getQueryParam('user_id') || 1)

    const overlayActive = ref(false)
    const dailyVisible = ref(false)
    const subVisible = ref(false)

    const subTitle = ref('')
    const subDescription = ref('')
    const subReward = ref(0)
    const subLink = ref('')
    const subTaskKey = ref('')
    const subClaimed = ref(false)

    const userData = ref({})
    const dailyGroups = ref([])
    const socialTasks = [
    { key: 'tg', label: 'Subscribe to us in telegram', link: 'https://t.me/yourchannel' },
    { key: 'x', label: 'Follow us on X', link: 'https://x.com/yourprofile' },
    { key: 'inst', label: 'Follow us on Instagram', link: 'https://instagram.com/yourprofile' },
    { key: 'yt', label: 'Subscribe to our YouTube channel', link: 'https://www.youtube.com/@TheKotBegemotWorld' },
    { key: 'part', label: 'Subscribe to our partner', link: 'https://partner-link.com' }
    ]

    function showOverlay() {
    overlayActive.value = true
    document.body.style.overflow = 'hidden'
    }

    function closeOverlay() {
    overlayActive.value = false
    dailyVisible.value = false
    subVisible.value = false
    document.body.style.overflow = ''
    }

    function showDailyBlock() {
    showOverlay()
    dailyVisible.value = true
    }

    function showSubBlock(task) {
    showOverlay()
    subVisible.value = true

    subTitle.value = task.label
    subDescription.value = `Subscribe and get 5000 coins`
    subReward.value = 5000
    subLink.value = task.link
    subTaskKey.value = task.key

    fetch(`/user_data?user_id=${userId.value}`)
        .then(res => res.json())
        .then(data => {
        userData.value = data
        subClaimed.value = data[`task_${task.key}_done`] || false
        })
    }

    function claimSocialTask() {
    if (subClaimed.value) return

    fetch('/claim_task_reward', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId.value, task: subTaskKey.value, reward: subReward.value })
    })
        .then(res => res.json())
        .then(response => {
        if (response.success) {
            window.open(subLink.value, '_blank')
            subClaimed.value = true
        } else {
            alert(response.message)
        }
        })
    }
    const rewardNotification = ref('')
    const showRewardNotification = ref(false)

    function showRewardMessage(amount) {
        rewardNotification.value = `Вы получили ${amount} монет!`
        showRewardNotification.value = true
        setTimeout(() => {
            showRewardNotification.value = false
        }, 2000)
    }

    function claimDailyReward(day) {
    if (day.status !== 'available') return

    fetch('/claim_daily_reward', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId.value })
    })
        .then(res => res.json())
        .then(response => {
        if (response.success) {
            showRewardMessage(response.reward)
            loadUserData()
        } else {
            alert(response.message)
        }
        })
    }

    function loadUserData() {
        fetch(`/user_data?user_id=${userId.value}`)
            .then(res => res.json())
            .then(data => {
                if (!data.success) return

                userData.value = data

                const now = Date.now()
                const lastClaim = data.last_reward_claim_date ? new Date(data.last_reward_claim_date).getTime() : 0
                const rewardIntervalMs = 1000 * 60 * 60 * 24

                const currentDay = data.daily_day || 1
                const claimed = data.daily_reward_claimed || false

                let canClaim = false
                let isSoon = false

                if (!claimed) {
                    if (!lastClaim) {

                        canClaim = true
                    } else {
                        const elapsed = now - lastClaim
                        if (elapsed >= rewardIntervalMs) {
                            canClaim = true
                        } else {
                            isSoon = true
                        }
                    }
                }

                const rewards = [5000, 10000, 15000, 20000, 25000, 30000, 50000]
                const daysData = rewards.map((reward, i) => {
                    const day = i + 1
                    let status = ''
                    let label = ''

                    if (day < currentDay) {
                        status = 'claimed'
                        label = 'Received'
                    } else if (day > currentDay) {
                        status = 'future'
                        label = 'Come back later'
                    } else {
                        // current day
                        if (claimed) {
                            status = 'claimed'
                            label = 'Received'
                        } else if (canClaim) {
                            status = 'available'
                            label = 'Claim now'
                        } else if (isSoon) {
                            status = 'soon'
                            label = 'Soon'
                        } else {
                            status = 'waiting'
                            label = 'Wait'
                        }
                    }

                    return { day, reward, status, label }
                })

                dailyGroups.value = [daysData.slice(0, 3), daysData.slice(3, 6), [daysData[6]]]
            })
    }





    onMounted(() => {
    loadUserData()
    })
</script>


<template>
  <div class="container">
    <div class="head"><h1>Tasks</h1></div>

    <div class="tasks" @click="showDailyBlock">
      <h2>Daily tasks</h2>
    </div>

    <div class="tasks" v-for="task in socialTasks" :key="task.key" @click="showSubBlock(task)">
      <h2>{{ task.label }}</h2>
    </div>

    <div class="task-overlay" v-if="overlayActive" @click="closeOverlay"></div>
    <transition name="fade-up">
        <div class="earn_block" v-if="dailyVisible">
        <div class="day" v-for="(group, index) in dailyGroups" :key="index">
            <div
            v-for="day in group"
            :key="day.day"
            :class="['days', { days7: day.day === 7 }, day.status ]"
            @click="claimDailyReward(day)"
            >
            <h1>{{ day.day }} day</h1>
            <div class="add">
                <p>{{ day.reward }}</p>
                <img src="/src/assets/coin.png" alt="Coin" class="coinday" />
            </div>
            <div class="label" v-if="day.label">{{ day.label }}</div>
            </div>
        </div>
        </div>
    </transition>
    <transition name="fade-up-sub">
        <div class="sub_block" v-if="subVisible">
        <h1>{{ subTitle }}</h1>
        <p class="upgrade-description">{{ subDescription }}</p>
        <div class="upgrade-footer">
            <img src="/src/assets/coin.png" alt="Coin" />
            <p class="upgrade-cost">{{ subReward }}</p>
        </div>
        <button class="upgrade-action" :disabled="subClaimed" @click="claimSocialTask">
            {{ subClaimed ? 'The award has already been received' : 'Get a reward' }}
        </button>
        </div>
    </transition>
  </div>
   <transition name="slide-up">
        <div class="reward-toast" v-if="showRewardNotification">
            {{ rewardNotification }}
        </div>
    </transition>

    

</template>

<style scoped>
    .container {
        display:block;
        margin:0 auto;
        margin-bottom:100px;
        justify-content: center;
        align-items: center;
        height:78%;
        background: #1e1e1e;
        border-radius: 30px 30px 30px 30px;
        padding-bottom:15px;
        box-shadow: 0px 0px 8px #6366F1;
        text-align: center;
        overflow-y: auto; 
        overflow-x: hidden;
    }

    .tasks {
        border: 1px solid #6366F1;
        box-shadow: 0px 0px 8px #6366F1;
        border-radius: 30px;
        padding: 0px;
        margin-bottom: 20px;
        font-size:15px;
        margin: 20px;

    }

    .earn_block {
        padding-top: 1%;
        position: fixed;
        bottom: 0;  
        display: flex;
        flex-direction: column;
        top: 35%;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        height: 60%;
        border: none;
        border-top: 1px solid #6366F1;
        border-radius: 30px 30px 0px 0px;
        background-color:#161516;
        z-index: 10;
        transition: all 1s;
        text-align: center;
        align-items: center;
    }

    .sub_block {
        padding-top: 1%;
        position: fixed;
        bottom: 0;  
        display: flex;
        flex-direction: column;
        top: 45%;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        height: 45%;
        border: none;
        border-top: 1px solid #6366F1;
        border-radius: 30px 30px 0px 0px;
        background-color:#1d1b1d;
        z-index: 10;
        transition: all 1s;
        text-align: center;
        align-items: center;
    }
    .upgrade-description {
        width: 80%;
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

    .upgrade-action {
        padding: 20px 40px;
        background-color:#773ffa8f;
        font-size: 22px;
        box-shadow: 0px 3px 8px #6366F1;
        border-radius: 15px;
        border: none;
    }

    .day {
        display: flex;
    }

    .days {
        background: #292929;
        padding: 20px 10px;
        margin: 5px;
        height: 50%;
        width: 50%;
        border-radius: 15px;
        box-shadow: 0 2px 4px #6366F1;
        text-align: center;
        align-items: center;
        color: white;
        font-family: Arial, sans-serif;
        margin-bottom: 10px;
    }

    .days7 {
        background: #292929;
        padding: 20px 60px;
        margin: 5px;
        border-radius: 15px;
        box-shadow: 0 2px 8px #6366F1;
        text-align: center;
        align-items: center;
        color: white;
        font-family: Arial, sans-serif;
        margin-bottom: 20px;
    }

    .days7 h1 {
        font-size: 25px;
        margin: 0px;
    }
    .days7 p {
        font-size: 20px;
        margin: 1px;
    }

    .days h1 {
        font-size: 25px;
        margin: 0px;
    }
    .days p {
        font-size: 20px;
        margin: 1px;
    }

    .task-overlay {
        display: flex;
        position: fixed;
        z-index: 9;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.5);
        backdrop-filter: blur(5px);
    }

    .past {
        opacity: 0.3;
        pointer-events: none;
    }
    .future {
        opacity: 0.5;
        pointer-events: none;
    }
    .claimed {
        background-color: #058d005d;
        pointer-events: none;
    }
    .available {
        cursor: pointer;
        box-shadow: 0 2px 4px #178800;
    }
    .soon {
        box-shadow: 0 2px 4px #884d00;
        pointer-events: none;
    }
    .label {
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        margin-top: 4px;
        color: #8B00FF;
    }


    .coinday {
        width: 20px;
        height: 20px;
    }

    .add {
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .reward-toast {
        position: fixed;
        top: 50px;
        left: 0;
        right: 0;
        margin: 0 auto;
        background: #530c8dc0;
        color: white;
        width: 60%;
        padding: 16px 24px;
        border-radius: 30px;
        font-size: 18px;
        box-shadow: 0px 0px 8px #6366F1;
        z-index: 1000;
        animation: bounceIn 0.4s ease;

    }
    .fade-up-enter-active, .fade-up-leave-active {
        transition: all 1s ;
    }
    .fade-up-enter-from,
    .fade-up-leave-to {
        top: 100%;
    }
    .fade-up-enter-to, .fade-up-leave-from {
        top: 35%;
    }

    .fade-up-sub-enter-active, .fade-up-sub-leave-active {
        transition: all 1s ;
    }
    .fade-up-sub-enter-from,
    .fade-up-sub-leave-to {
        top: 100%;
    }
    .fade-up-sub-enter-to, .fade-up-sub-leave-from {
        top: 45%;
    }

    @keyframes bounceIn {
    0% {
        transform: translateY(-100%);
        opacity: 0;
    }
    60% {
        transform: translateY(10px);
        opacity: 1;
    }
    100% {
        transform: translateY(0);
    }
    }

    .slide-up-enter-active,
    .slide-up-leave-active {
        transition: opacity 0.5s, transform 0.5s;
    }

    .slide-up-enter-from,
    .slide-up-leave-to {
        opacity: 0;
        transform: translateY(-100%);
    }

    .slide-up-enter-to,
    .slide-up-leave-from {
        opacity: 1;
        transform: translateY(0);
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
</style>
