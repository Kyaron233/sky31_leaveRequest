let activityTyleEle = document.querySelector('.activity_type span')
let activityTyleInput = document.querySelector('.activity_type input')
let typeOptions = document.querySelector('.type .type_options')
let yearOptions = document.querySelector('.year .date_options')
let monthOptions = document.querySelector('.month .options')
let dayOptions = document.querySelector('.day .options')
let hourOptions = document.querySelector('.hour .options')

// 判断是发布还是修改

// 选择类型
function check(e) {
  // 获取选择结果
  let result = e.innerText
  let options = e.parentElement
  // 高亮显示
  // 取消原本的高亮
  options.querySelector('.checked')?.classList.remove('checked')
  e.classList.add('checked')
  // 将结果展示到页面上
  options.parentElement.querySelector('span').innerHTML = result

  // 将结果同步给接收数据的input标签
  if (options.classList.contains('type_options')) {
    activityTyleInput.value = result
  }
}

// 监听点击事件控制选项框显示和隐藏
document.addEventListener('click', e => {
  // 类型选项框
  let ele = e.target
  if (!(typeOptions.classList.contains('hide') || ele.closest('.type_options'))) {
    // 类型选项框显示期间，点击选项框外部时隐藏选项框
    activityTyleEle.classList.toggle('active')
    typeOptions.classList.toggle('hide')
  } else if (!(yearOptions.classList.contains('hide') || ele.closest('.year .date_options'))) {
    // 年份选项框显示期间，点击选项框外部时隐藏选项框
    yearOptions.classList.toggle('hide')
  } else if (!(monthOptions.classList.contains('hide') || ele.closest('.month .date_options'))) {
    // 月份选项框显示期间，点击选项框外部时隐藏选项框
    monthOptions.classList.toggle('hide')
  } else if (!(dayOptions.classList.contains('hide') || ele.closest('.day .date_options'))) {
    // 日期选项框显示期间，点击选项框外部时隐藏选项框
    dayOptions.classList.toggle('hide')
  } else if (!(hourOptions.classList.contains('hide') || ele.closest('.hour .date_options'))) {
    // 小时选项框显示期间，点击选项框外部时隐藏选项框
    hourOptions.classList.toggle('hide')
  } else if (ele.closest('.activity_type span')) {
    // 点击到类型一栏时改变选项框存在状态
    activityTyleEle.classList.toggle('active')
    typeOptions.classList.toggle('hide')
  } else if (ele.closest('.year')) {
    // 点击到年一栏时改变选项框存在状态
    yearOptions.classList.toggle('hide')
  } else if (ele.closest('.month')) {
    // 点击到月一栏时改变选项框存在状态
    monthOptions.classList.toggle('hide')
  } else if (ele.closest('.day')) {
    // 点击到日期一栏时改变选项框存在状态
    dayOptions.classList.toggle('hide')
  } else if (ele.closest('.hour')) {
    // 点击到小时一栏时改变选项框存在状态
    hourOptions.classList.toggle('hide')
  }

  // 事件委托：选择
  if (e.target.closest('.options')) {
    check(e.target)
  }
})

// 发布新活动并将数据提交给服务器
let issueBtn = document.querySelector('.issue_btn')
issueBtn.addEventListener('click', () => {
  // 获取数据并提交
  let activityForm = document.querySelector('.activity_form')
  let activityData = serialize(activityForm, { hash: true, empty: true })
  console.log(activityData)
  // 获取时间并处理格式
  let year = document.querySelector('.year span').innerHTML
  let month = document.querySelector('.month span').innerHTML || 1
  let day = document.querySelector('.day span').innerHTML || 1
  let hour = document.querySelector('.hour span').innerHTML || 0
  console.log(month, day, hour)
  let date = `${year}-${month >= 10 ? month : '0' + month}-${day >= 10 ? day : '0' + day} ${hour >= 10 ? hour : '0' + hour}:00:00`
  console.log(date)
  // 提交到服务器
  if (location.href.split('#')[1] === 'issueNewActivity') {
    axios({
      method: 'post',
      url: '/publish/add',
      data: {
        ...activityData,
        event_date: date
      }
    })
      .then(result => {
        console.log(result)
        popupTop.innerHTML = '发布成功！'
        popup.classList.remove('hide')
      })
      .catch(err => {
        console.dir(err)
        popupTop.innerHTML = '发布失败！'
        popup.classList.remove('hide')
      })
  } else {
    let event_id = location.href.split('=')[1]
    axios({
      method: 'patch',
      url: `/publish/${event_id}`,
      data: {
        ...activityData,
        event_date: date
      }
    })
      .then(result => {
        console.log(result)
        popupTop.innerHTML = '发布成功！'
        popup.classList.remove('hide')
      })
      .catch(err => {
        console.dir(err)
        popupTop.innerHTML = '发布失败！'
        popup.classList.remove('hide')
      })
  }
})
