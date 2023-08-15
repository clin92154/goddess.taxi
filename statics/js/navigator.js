//javascript.js
//set map options
let map,
  directionsService,
  computeHeading,
  isLocationOnEdge,
  directionsDisplay,
  encodePath,
  decodePath,
  arrivalInfoAP,
  geocoder; //Map api宣告變數

let stepsPath = []; //路線暫存
let currentStepIndex = 1; // 目前所在步驟的索引
let currentStep = null; // 目前所在步驟
let nextStep = null; // 下一個步驟
let nextPoint = null; // 行徑方向下一個點座標
let mapRotation = 0; // 地圖旋轉角度
let NowLatLng = null; // 目前所在位置
let endPosition = null; // 目的地位置
let positionRecord = []; // 紀錄移動路徑的陣列
let Pathpolyline = null; // 移動路徑的線段
let estimatedDistance = 0; // 預估距離
let moveDistance = 0; // 移動距離
let totalMoveLength = 0; // 移動路徑的總長度
let idlePosition = null; // 怠速開始位置
let idleTimer = 0; // 計時器
let startIdletime = null; // 怠速起始時間
let endIdletime = null; // 怠速結束時間
let nowposition = null; // 目前所在位置
const cardTextDistance = document.querySelector("#card-distance");
const cardTextInstruction = document.querySelector("#card-instruction");
const cardTextFare = document.querySelector("#card-fare");
let routeData; // 路線資料
let watchPositionId; // 監聽位置的 ID
let fare = 0; // 車資
const totalDistanceElement = document.getElementById("total-distance");
const totalFareElement = document.getElementById("total-fare");
const arrivalInfo = document.getElementById("arriavalInput");
const departureInfo = document.getElementById("departure");
const APoptions = {
  componentRestrictions: { country: "tw" },
  fields: ["place_id"],
}; //autocomplete設定

//初始化地圖
let marker;
let startModal = new bootstrap.Modal(document.getElementById("startModal"));
let endModal = new bootstrap.Modal(document.getElementById("endModal"));

function initMap() {
  const initLatLng = { lat: 25.0475613, lng: 121.5173399 };
  const mapOptions = {
    zoom: 18, //放大的倍率
    center: initLatLng, //初始化的地圖中心位置
    mapTypeControl: false, //地圖樣式控制項
    fullscreenControl: true, //全螢幕控制項
    rotateControl: false, //旋轉控制項
    scaleControl: false, //比例尺控制項
    streetViewControl: false, //街景控制項
    zoomControl: true, //縮放控制項
    tilt: 0, //地圖傾斜角度
    mapId: "930dcea21763fbb0", //地圖樣式
    //mapTypeId:'hybrid'
  };
  map = new google.maps.Map(document.getElementById("googleMap"), mapOptions);

  //初始化direction API
  directionsService = new google.maps.DirectionsService();
  //宣告計算角度函數
  computeHeading = google.maps.geometry.spherical.computeHeading;
  //宣告計算距離函數
  // const computeDistance = google.maps.geometry.spherical.computeDistanceBetween;
  //宣告判斷點是否在線段上的函數
  isLocationOnEdge = google.maps.geometry.poly.isLocationOnEdge;
  //宣告編碼路徑函數
  encodePath = google.maps.geometry.encoding.encodePath;
  //宣告解碼路徑函數
  decodePath = google.maps.geometry.encoding.decodePath;
  //初始化autocomplete
  if (arrivalInfo) {
    arrivalInfoAP = new google.maps.places.Autocomplete(arrivalInfo, APoptions);
    arrivalInfoAP.addListener("place_changed", function () {
      let place_id = arrivalInfoAP.getPlace().place_id;
      geocoder
        .geocode({ placeId: place_id })
        .then(({ results }) => {
          arrivalInfo.value = results[0].formatted_address;
          arrivalLatLng = results[0].geometry.location;
        })
        .catch((e) => window.alert("Geocoder failed due to: " + e));
    });
  }
  //初始化geocoder
  geocoder = new google.maps.Geocoder();
  //初始化路線顯示
  directionsDisplay = new google.maps.DirectionsRenderer({
    preserveViewport: true,
    draggable: false,
    suppressMarkers: true,
    polylineOptions: {
      strokeColor: "#004B97", // set the color of the route
      strokeWeight: 6, // set the width of the line of the route
    },
  });
  //0726更新，如果訂單資料庫中行程出發時間(start_at)存在，則將怠速開始時間設為start_at,否則設為現在時間
  if (start_at) {
    //0726更新,JS中有使用到時間的格式均為Unix Timestamp，因此需要將start_at轉換為Unix Timestamp
    //0726更新,時間格式參考,start_at = "2023-07-31 12:34:56";
    startIdletime = new Date(start_at).getTime();
  } else {
    startIdletime = Date.now();
  }
  getPosition();
}

function addMarker(location, label) {
  // 創建標記
  for (i = 0; i <= location.length - 1; i++) {
    marker = new google.maps.Marker({
      position: location[i],
      map: map,
      label: label,
    });

    // 設置定時器，3 秒後清除標記
    setTimeout(function () {
      marker.setMap(null);
    }, 3000);
  }
}

function showToast(message, duration = 5000) {
  // 建立 Toast 元素
  let toastElement = document.createElement("div");
  toastElement.classList.add("toast");
  toastElement.classList.add("show");

  // 設定 Toast 的內容
  toastElement.innerHTML = `
      <div class="toast-header">
        <strong class="me-auto">程式通知</strong>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    `;

  // 將 Toast 元素加入到容器中
  document.getElementById("toastContainer").appendChild(toastElement);

  // 顯示 Toast 一段時間後自動隱藏
  setTimeout(function () {
    toastElement.remove();
  }, duration);
}

//校正API計算出來的角度成為地圖用的0~360度
function headingCorrection(heading) {
  if (heading < 0) {
    heading += 360;
  }
  return heading;
}

// 轉換距離單位
function formatDistance(distance) {
  if (distance >= 1000) {
    // 大於等於1000公尺，轉換為公里，並保留小數點後1位
    const kilometers = (distance / 1000).toFixed(1);
    return kilometers + " 公里";
  } else {
    // 小於1000公尺，直接使用公尺單位
    return distance + " 公尺";
  }
}

// 計算兩點距離
function computeDistance(latLng1, latLng2) {
  const R = 6371000; // 地球半徑，單位為公尺
  const lat1 = latLng1.lat();
  const lon1 = latLng1.lng();
  const lat2 = latLng2.lat();
  const lon2 = latLng2.lng();
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) *
      Math.cos(deg2rad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = Math.floor(R * c); // 距離單位為公尺
  return distance;
}

// 角度轉弧度
function deg2rad(deg) {
  return deg * (Math.PI / 180);
}

//將座標取到小數點第3位
function LatLngtoFloor(number) {
  //位數可嘗試取到小數點第5位
  let factor = Math.pow(10, 5); // 10^3 = 1000
  let truncatedNumber = Math.floor(number * factor) / factor;
  return truncatedNumber;
}

//取得WatchPosition權限後執行
function recordPosition(position) {
  let currentStep = routeData.legs[0].steps[currentStepIndex]; // 目前所在步驟
  if (currentStepIndex < routeData.legs[0].steps.length - 1) {
    // 如果目前步驟不是最後一步，則取得下一步驟
    nextStep = routeData.legs[0].steps[currentStepIndex + 1]; // 下一步驟
  } else {
    // 如果目前步驟是最後一步，則下一步驟為空值
    nextStep = null;
  }
  NowLatLng = new google.maps.LatLng(
    LatLngtoFloor(position.coords.latitude),
    LatLngtoFloor(position.coords.longitude)
  );
  console.log(NowLatLng.toString());
  //如果positionRecord陣列具有數值，則寫入現在位置與上一個位置的距離
  if (positionRecord[positionRecord.length - 1]) {
    moveDistance = computeDistance(
      positionRecord[positionRecord.length - 1],
      NowLatLng
    );
    // showToast("移動距離" + moveDistance);
  }
  if (positionRecord[positionRecord.length - 1] !== NowLatLng) {
    // 如果現在位置與上一個位置不同，則寫入現在位置
    positionRecord.push(NowLatLng);
  }
  if (moveDistance <= 5 && startIdletime == null) {
    // 如果現在位置與上一個位置距離<=5公尺，則寫入待機開始時間
    startIdletime = Date.now();

    idlePosition = NowLatLng;
    showToast("開始待機" + startIdletime);
  } else if (moveDistance > 5 && startIdletime != null) {
    // 如果現在位置與上一個位置距離>5公尺且開始怠速時間不為空值，則寫入待機結束時間
    endIdletime = Date.now();

    // showToast(idlePosition.equals(NowLatLng) + " " + idlePosition + " " + NowLatLng);
    showToast("結束待機" + endIdletime);
    // 計算待機時間
    idleTimer += Math.floor((endIdletime - startIdletime) / 1000);
    // 清空待機時間
    showToast("待機時間" + idleTimer + "秒");
    startIdletime = null;
    endIdletime = null;
  }
  positionRecord.forEach((currentValue, index) => {
    if (index > 0) {
      const previousPoint = positionRecord[index - 1];
      const distance = computeDistance(previousPoint, currentValue);
      estimatedDistance += distance;
      if (index === positionRecord.length - 1) {
        estimatedDistance = Math.floor(estimatedDistance / 1000);
      }
    }
  });
  if (cardTextFare) {
    cardTextFare.innerHTML =
      "目前車資：" +
      (50 + Math.floor(idleTimer / 60) * 2 + estimatedDistance * 20) +
      "元";
  }
  // 計算現在位置與路徑結果座標中最近點之間的角度
  let heading = headingCorrection(
    computeHeading(
      NowLatLng,
      findNextPointsToCurrentLocationTest(NowLatLng, routeData.overview_path)
    )
  );
  // 計算現在位置與路徑結果座標中最近座標之間的距離
  let distance = computeDistance(NowLatLng, currentStep.start_location);
  //判定是否在線段(全段路徑)內
  nowposition.setPosition(NowLatLng);
  map.setHeading(heading);
  map.setCenter(NowLatLng);
  map.setZoom(17);
  map.setTilt(80);

  if (isLocationOnEdge(NowLatLng, Pathpolyline, 0.0003)) {
    let stepPath = decodePath(stepsPath[currentStepIndex]);
    let stepPolyline = new google.maps.Polyline({
      path: stepPath,
    });
    // console.log(stepPath);
    // addMarker(stepPath);
    // 如果現在位置離現在步驟結束點<50公尺，且目前步驟線段內且未到達最後步驟，則設定地圖角度為目前步驟終點座標與下一步驟終點座標間的角度
    if (isLocationOnEdge(NowLatLng, stepPolyline, 0.0003)) {
      // 計算現在位置與下個步驟起點座標間的距離
      if (currentStepIndex < stepsPath.length - 1) {
        currentStepIndex++;
        let distance = computeDistance(NowLatLng, nextStep.start_location);
        cardTextDistance.innerHTML = formatDistance(distance) + "後";
        cardTextInstruction.innerHTML = nextStep.instructions;
        //showToast("在線段內且未到達最後步驟");
      } else {
        cardTextDistance.innerHTML = formatDistance(distance) + "後";
        cardTextInstruction.innerHTML = currentStep.instructions;
        /*if (distance <= 10) {
                                                                                                                                                                                                endJourney();
                                                                                                                                                                                                endmodal.show();
                                                                                                                                                                                                showToast("到達目的地");}*/
      }
    } else {
      //如果不屬於上述情況，則刷新導覽卡片內容
      cardTextDistance.innerHTML = formatDistance(distance) + "後";
      cardTextInstruction.innerHTML = currentStep.instructions;
    }
  } else {
    // 如果現在位置不在目前步驟線段內，則將起點設為現在位置，終點設為目的地，並重新計算路線
    // 路線設定
    calcRoute(NowLatLng, arrivalLatLng);
    map.setCenter(NowLatLng);
    showToast("偏離路徑");
  }
}

// 获取定位信息失败时输出错误信息到控制台
function showError(error) {
  showToast("Error getting location: " + error.message);
}
// 每隔5秒获取一次定位信息並比較路徑偏移
function startJourney() {
  map.setTilt(80);
  map.setZoom(18);
  //0726更新,如果startIdletime不為空值，則計算待機時間，須注意startIdletime時間格式需要是毫秒
  if (startIdletime != null) {
    endIdletime = Date.now();
    idleTimer += Math.floor((endIdletime - startIdletime) / 1000);
    showToast("待機時間" + idleTimer + "秒");
    // 清空起始及結束待機時間
    startIdletime = null;
    endIdletime = null;
  }
  watchPositionId = navigator.geolocation.watchPosition(
    recordPosition,
    showError,
    { timeout: 2 * 1000, maximumAge: 0, enableHighAccuracy: true }
  );
}
// 停止定位
function endJourney() {
  navigator.geolocation.clearWatch(watchPositionId);
  // 計算總距離
  positionRecord.forEach((currentValue, index) => {
    if (index > 0) {
      const previousPoint = positionRecord[index - 1];
      const distance = computeDistance(previousPoint, currentValue);
      totalMoveLength += distance;
      if (index === positionRecord.length - 1) {
        totalMoveLength = Math.floor(totalMoveLength / 1000);
      }
    }
  });
  // 計算總車資
  idleTimer = Math.floor(idleTimer / 60);
  showToast("結算中...");
  final_time = idleTimer;
  final_distance = totalMoveLength;

  if (totalDistanceElement && totalFareElement) {
    final_fare = base_fare + idleTimer * 2 + totalMoveLength * 20;
    totalDistanceElement.innerText = final_distance + " 公里";
    if (final_fare < 100 || isNaN(final_fare)) {
      final_fare = 100;
    }
    totalFareElement.innerText = final_fare + " 元";
  }
  // 儲存資料內容
  //departing的資料取自於positionRecord的第一個座標點
  geocoder.geocode({ location: positionRecord[0] }).then(({ results }) => {
    departing = {
      name: results[0].formatted_address,
      lati_NS: results[0].geometry.location.lat(),
      longi_EW: results[0].geometry.location.lng(),
    };
  });
  //arriving的資料取自於資料庫傳入的arrivalLatLng
  geocoder
    .geocode({ location: positionRecord[positionRecord.length - 1] })
    .then(({ results }) => {
      arriving = {
        name: results[0].formatted_address,
        lati_NS: results[0].geometry.location.lat(),
        longi_EW: results[0].geometry.location.lng(),
      };
    });
  route_map = createMapUrl(positionRecord);
}

//歷史路徑圖片生成
function createMapUrl(locationRecord) {
  const apiKey = "AIzaSyBpLruvn_7H-6Q9gYl8LNGhVTm4kR5_2HY";
  console.log(locationRecord);
  const points = locationRecord
    .map((location) => `${location.lat()},${location.lng()}`)
    .join("|");

  const imageUrl = `https://maps.googleapis.com/maps/api/staticmap?size=640x480&path=color:0x0000ff|weight:5|${points}&key=${apiKey}`;
  console.log(imageUrl);
  return imageUrl;
}

//尋找路徑中的下一個點
function findNextPointsToCurrentLocationTest(currentLocation, overviewPath) {
  // 假设有 10 组座标点，每两组座标点构成一段折线
  const coordinates = overviewPath; //路徑全部座標點
  const currentPoint = currentLocation; //現在位置座標點
  // 每兩組座標為一線段
  for (let i = coordinates.length - 1; i >= 0; i -= 1) {
    let startPoint = coordinates[i];
    let endPoint = coordinates[i - 1];
    console.log(startPoint.lat() + "," + startPoint.lng() + "index :" + i);
    console.log(endPoint.lat() + "," + endPoint.lng() + "index :" + (i - 1));
    // 创建当前折线段的 Polyline 对象
    const polyline = new google.maps.Polyline({
      path: [startPoint, endPoint], // 设置当前折线段的坐标点数组
      geodesic: true, // 设置为大地曲线折线
    });
    if (isLocationOnEdge(currentPoint, polyline, 0.0003)) {
      addMarker(startPoint, "T");
      console.log(startPoint.lat() + "," + startPoint.lng());
      return startPoint;
    } else {
      continue;
    }
  }
  addMarker(overviewPath[1], "O");
  return overviewPath[1];
}

// 計算前一座標與現在座標的方向並產生估算的下一座標
function computeOffsetLatLng(currentLocation) {
  let latestRecord = positionRecord[positionRecord.length - 2];
  let heading = headingCorrection(
    computeHeading(latestRecord, currentLocation)
  );
  let offsetLatLng = google.maps.geometry.spherical.computeOffset(
    currentLocation,
    50,
    heading
  );
  addMarker(offsetLatLng, "F");
  return offsetLatLng;
}
// 取得現在位置
function getPosition() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
      let latLng = new google.maps.LatLng(
        position.coords.latitude,
        position.coords.longitude
      );
      departureLatLng = latLng;
      map.setZoom(18);
      map.setTilt(80);
      map.setCenter(latLng);
      if (nowposition == null) {
        nowposition = new google.maps.Marker({
          position: latLng,
          map: map,
          icon: arrow,
        });
      } else {
        nowposition.setMap(null);
        nowposition = new google.maps.Marker({
          position: latLng,
          map: map,
          icon: arrow,
        });
      }
    });
    if (arrivalInfo) {
      arrivalInfo.value = arrivalLatLng;
    } else if (departureInfo) {
      departureInfo.value = arrivalLatLng;
    }

    startModal.show();
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function calcRoute(origin, destination) {
  //接收來自後端之起點與終點
  let request = {
    origin: origin,
    destination: destination,
    travelMode: google.maps.TravelMode.DRIVING, //路徑類型
    unitSystem: google.maps.UnitSystem.MERTRIC, //路徑距離單位
  };
  //使用 DirectionsService 物件來取得路徑
  directionsService.route(request, function (result, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      //讀取路徑資訊
      routeData = result.routes[0];
      console.log(routeData);
      //紀錄路徑比較定位用路徑資訊
      Pathpolyline = new google.maps.Polyline({
        path: routeData.overview_path,
      });
      cardTextDistance.innerHTML =
        routeData.legs[0].steps[1].distance.text + "後";
      cardTextInstruction.innerHTML = routeData.legs[0].steps[1].instructions;
      let steps = result.routes[0].legs[0].steps;
      let StepInstruction = [];
      steps.forEach((step) => {
        const instruction = step.instructions;
        const path = encodePath(step.path);
        StepInstruction.push(instruction);
        stepsPath.push(path);
      });

      // 繪製路線
      directionsDisplay.setDirections(result);
      directionsDisplay.setMap(map);
      map.setZoom(18);
      map.setTilt(80);
    } else {
      //清空路徑
      directionsDisplay.setDirections({ routes: [] });
      //預設地圖中心位置為台北車站
      map.setTilt(10);
      map.setZoom(10);
      map.setCenter(initLatLng);
      //show error message
      showToast("Directions request failed due to " + status);
    }
  });
}

window.initMap = initMap;
