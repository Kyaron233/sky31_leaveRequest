// 获取按姓名分类时的数据
function getDetailsByName() {
  axios({
    url: `query/history/${location.href.split('=')[1]}`
  })
    .then(result => {
      console.log(result)
      let memberMessages = result.data

      // 渲染成员列表
      let memberItems = document.querySelector('.user_items')
      // 先清空成员列表
      memberItems.innerHTML = `
        <li class="lhead">正主席 / 团支书</li>
        <li class="lhead">分管主席</li>
        <li class="lhead">正部</li>
        <li class="lhead">副部</li>
        <li class="lhead">干事</li>
        `
      let lheads = memberItems.querySelectorAll('.lhead')
      // 用以判断各个lhead后有没有lbody，没有的隐藏
      let isDisplays = [0, 0, 0, 0, 0]
      memberMessages.forEach(memberMessage => {
        if (memberMessage.name.length === 2) {
          memberMessage.name = memberMessage.name.split('').join('&nbsp;&nbsp;')
        }

        let li = document.createElement('li')
        li.classList.add('lbody')
        li.innerHTML = `<span class="name" id="${memberMessage.student_id}">${memberMessage.name}</span>`
        let rid = memberMessage.role_in_depart
        if (rid === 4) {
          memberItems.insertBefore(li, lheads[1])
        } else if (rid === 3) {
          memberItems.insertBefore(li, lheads[2])
        } else if (rid === 2) {
          memberItems.insertBefore(li, lheads[3])
        } else if (rid === 1) {
          memberItems.insertBefore(li, lheads[4])
        } else {
          memberItems.appendChild(li)
        }
        let id = Math.abs(rid - 4)
        isDisplays[id] = 1
      })
      for (let i = 0; i < isDisplays.length; i++) {
        isDisplays[i] || lheads[i].classList.add('hide')
      }

      // console.log(memberItems)
      // 将成员信息存入内存，在页面刷新时获取并展示
      // localStorage.setItem('memberItems', memberItems.outerHTML)
    })
    .catch(error => {
      console.dir(error)
    })
}

// 获取按部门分类时的数据
function getDetailsByDepartment() {
  axios({
    url: `query/history/department/${location.href.split('=')[1]}`
  })
    .then(result => {
      console.log(result)
      let data = result.data
      // 获取到活动列表
      let items = document.querySelector('.classified_by_department .activity_items')
      // 先清空活动列表
      items.innerHTML = ''
      data.forEach(activeData => {
        // 转换时间格式
        let date = new Date(activeData.event_date)
        const formattedDate = date.toISOString().split('T')[0].split('-').join('.')
        let li = document.createElement('li')
        li.classList.add('item')
        li.id = activeData.event_id
        li.innerHTML = ` 
        <div class="activity_name">${activeData.event_name}</div>
        <span style="display: none;">${activeData.event_type}</span>
        <div class="expiration_date"><span class="date">${formattedDate}</span><span>（截止时间）</span></div>
      `
        if (!activeData.isActive) {
          li.classList.add('ended')
        }
        items.appendChild(li)
      })
    })
    .catch(error => {
      console.dir(error)
    })
}

// 获取某个成员的请假详情
function getUserDetails(student_id) {
  axios({
    url: `query/history/student/${student_id}`
  })
    .then(result => {
      console.log(result)
      let data = result.data
      // 获取到活动列表
      let items = document.querySelector('.user_request_forms .activity_items')
      // 先清空活动列表
      items.innerHTML = ''
      data.forEach(activeData => {
        if (!activeData.is_permitted) {
          return
        }
        // 转换时间格式
        let date = new Date(activeData.event_date)
        const formattedDate = date.toISOString().split('T')[0].split('-').join('.')
        let li = document.createElement('li')
        li.classList.add('item')
        li.innerHTML = ` 
        <div class="activity_name">${activeData.whoLeave_event}</div>
        <div class="expiration_date"><span class="date">${formattedDate}</span><span>（截止时间）</span></div>
      `
        if (!activeData.isActive) {
          li.classList.add('ended')
        }
        items.appendChild(li)
      })
      // 若有内容则隐藏背景图
      if (items.innerHTML) {
        document.querySelector('.user_request_forms').classList.add('nobg')
      }
    })
    .catch(error => {
      console.dir(error)
    })
}

// 获取某个活动的请假详情
function getActivityDetails(event_id) {
  let department_id = location.href.split('=')[1]
  console.log(department_id, event_id)
  axios({
    url: '/query/history/department',
    params: {
      department_id,
      event_id
    }
  })
    .then(result => {
      console.log(result)
      let memberMessages = result.data

      // 渲染成员列表
      let memberItems = document.querySelector('.requested_users .user_items')
      // 先清空成员列表
      memberItems.innerHTML = `
        <li class="lhead">正主席 / 团支书</li>
        <li class="lhead">分管主席</li>
        <li class="lhead">正部</li>
        <li class="lhead">副部</li>
        <li class="lhead">干事</li>
        `
      let lheads = memberItems.querySelectorAll('.lhead')
      // 用以判断各个lhead后有没有lbody，没有的隐藏
      let isDisplays = [0, 0, 0, 0, 0]
      memberMessages.forEach(memberMessage => {
        if (!memberMessage.is_permitted) {
          return
        }
        if (memberMessage.whoLeave_name.length === 2) {
          memberMessage.whoLeave_name = memberMessage.whoLeave_name.split('').join('&nbsp;&nbsp;')
        }

        let li = document.createElement('li')
        li.classList.add('lbody')
        li.innerHTML = `<span class="name">${memberMessage.whoLeave_name}</span>`
        let rid = memberMessage.whoLeave_role
        if (rid === 4) {
          memberItems.insertBefore(li, lheads[1])
        } else if (rid === 3) {
          memberItems.insertBefore(li, lheads[2])
        } else if (rid === 2) {
          memberItems.insertBefore(li, lheads[3])
        } else if (rid === 1) {
          memberItems.insertBefore(li, lheads[4])
        } else {
          memberItems.appendChild(li)
        }
        let id = Math.abs(rid - 4)
        isDisplays[id] = 1
      })
      for (let i = 0; i < isDisplays.length; i++) {
        isDisplays[i] || lheads[i].classList.add('hide')
      }
    })
    .catch(error => {
      console.dir(error)
    })
}
