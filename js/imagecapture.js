(function () {
  "use strict";

  const ui = {
    templates: {
      icons: {
        camera: `<svg width="18" height="18" class="svg-inline--fa" fill="#FFF" style="height: 18px; vertical-align: text-bottom" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path d="M397 550a115 115 0 1 0 230 0 115 115 0 1 0-230 0"/><path d="M835 320H726c-9.2 0-17.8-4-24-10.8-56.8-63.6-78.2-85.2-101.4-85.2h-171c-23.4 0-46.4 21.6-103.4 85.4-6 6.8-14.8 10.6-23.8 10.6h-8.2v-16c0-8.8-7.2-16-16-16h-52c-8.8 0-16 7.2-16 16v16h-15c-35.4 0-67.2 26.4-67.2 61.4v352c0 35 31.8 66.6 67 66.6h640c35.2 0 61-31.6 61-66.6v-352c0-35-25.8-61.4-61-61.4M520 720.8c-100.6 4.6-183.4-78.2-178.8-178.8 4-87.8 75-158.8 162.8-162.8 100.6-4.6 183.4 78.2 178.8 178.8-4 87.8-75 158.8-162.8 162.8M704 436c-14.4 0-26-11.6-26-26s11.6-26 26-26 26 11.6 26 26-11.6 26-26 26"/></svg>`,
      },
      toast: {
        top: `<div class="fade toast success show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header"><span class="mr-auto"></span><button type="button" class="close ml-2 mb-1" data-dismiss="toast"><span aria-hidden="true">×</span><span class="sr-only">Close</span></button></div>
            <div class="toast-body">`,
        bottom: `</div>
          </div>`,
      },
      modals: {
        scanning: `<div role="dialog" aria-modal="true" class="fade ModalComponent modal show" tabindex="-1" style="display: block">
          <div class="modal-dialog scrape-query-dialog modal-xl">
            <div class="modal-content">
              <div class="modal-header"><span>Working...</span></div>
              <div class="modal-body">
                <div class="row justify-content-center">
                <h3>Creating Capture...</h3>
                </div>
              </div>
              <div class="ModalFooter modal-footer">
                <div>
                  <button id="modal_cancel" type="button" class="ml-2 btn btn-secondary">Close</button>
                </div>
              </div>
            </div>
          </div>
        </div>`,
        error: {
          top: `<div role="dialog" aria-modal="true" class="fade ModalComponent modal show" tabindex="-1" style="display: block; overflow: auto">
            <div class="modal-dialog scrape-query-dialog modal-xl">
              <div class="modal-content">
                <div class="modal-header"><span>Error</span></div>
                <div class="modal-body">
                  <div class="row justify-content-center">`,
          bottom: `</div>
                    </div>
                  <div class="ModalFooter modal-footer">
                    <div>
                      <button id="modal_cancel" type="button" class="ml-2 btn btn-secondary">Close</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>`,
        },
      },
    },
    styles: {
      ".tagger-tabs": {
        position: "absolute",
        flex: "0 0 450px",
        "max-width": "450px",
        "min-width": "450px",
        height: "100%",
        overflow: "auto",
        order: -1,
        "background-color": "var(--body-color)",
        "z-index": 10,
      },
      ".tagger-tabs > .modal-dialog > .modal-content": {
        "max-height": "100vh",
      },
      ".tagger-tabs > .modal-dialog > .modal-content > .modal-body": {
        "overflow-y": "auto",
        "max-height": "calc(100vh - 300px)",
      },
    },
  };

  /**
   * Displays a custom alert if the user tries to navigate away from the page.
   * @param {Event} e - The event object.
   * @returns {string} - The warning message.
   */
  function warnUnload(e) {
    // Custom warning message (note that modern browsers might not display the message)
    const warningMessage = "Are you sure you want to leave this page?";
    e.preventDefault();
    e.returnValue = warningMessage; // Chrome requires returnValue to be set
    return warningMessage;
  }

  /**
   * Removes the beforeunload event listener.
   * @returns {void}
   */
  function removeWarn() {
    window.removeEventListener("beforeunload", warnUnload);
  }

  /**
   * Displays loading notice.
   */
  function display_notice() {
    var modal = ui.templates.modals.scanning;
    $("body").append(modal);

    $("#modal_cancel").one("click", function () {
      close_modal();
    });
  }

  /**
   * Displays error modal
   * @param {String} message error message
   */
  function display_error(message) {
    var toast = ui.templates.toast,
      insert = "<p>" + message + "</p>";

    $("body").append(toast.top + insert + toast.bottom);
  }

  /**
   * The close_modal function removes the modal component from the DOM.
   * @return The removal of the modalcomponent class
   */
  function close_modal() {
    $(".ModalComponent").remove();
  }

  /**
   * Waits for an element to appear in the DOM.
   * @param {string} selector - The selector for the element to wait for.
   * @returns {Promise<Element>} - A promise that resolves with the element.
   */
  function waitForElm(selector) {
    return new Promise((resolve) => {
      if (document.querySelector(selector)) {
        return resolve(document.querySelector(selector));
      }

      const observer = new MutationObserver((mutations) => {
        if (document.querySelector(selector)) {
          resolve(document.querySelector(selector));
          observer.disconnect();
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });
    });
  }

  /**
   * Builds a CSS string from a styles object.
   * @param {Object} styles - The styles object.
   * @returns {string} - A CSS string.
   */
  function buildStyles(styles) {
    let cssString = "";
    for (const selector in styles) {
      cssString += selector + " { ";
      for (const property in styles[selector]) {
        cssString += property + ": " + styles[selector][property] + "; ";
      }
      cssString += "} ";
    }
    return cssString;
  }

  /**
   * Returns an array containing the scenario and scenario ID extracted from the current URL.
   * @returns {Array<string>} An array containing the scenario and scenario ID.
   */
  function getScenarioAndID() {
    var result = document.URL.match(/(scenes|images)\/(\d+)/);
    var scenario = result[1];
    var scenario_id = result[2];
    return [scenario, scenario_id];
  }

  /**
   * Retrieves the metadata associated with a given scene ID.
   *
   * @param {string} scene_id - The ID of the scene to retrieve tags for.
   * @returns {Promise<string[]>} - A promise that resolves with an array of tag IDs.
   */
  async function getSceneMetadata(scene_id) {
    const reqData = {
      query: `{
        findScene(id: "${scene_id}") {
          id
          date
          files {
            frame_rate
            path
          }
          tags {
            id
          }
          galleries {
            id
          }
        }
      }`,
    };
    var result = await stash.callGQL(reqData);
    return {
      ...result.data.findScene,
      tags: result.data.findScene.tags.map((p) => p.id),
      galleries: result.data.findScene.galleries.map((p) => p.id),
    };
  }

  /**
   * Finds images by path.
   * @param {string} file_path - The path of the image to find.
   * @returns {Promise<Object>} - A promise that resolves with the image object.
   */
  async function findImagesByPath(file_path) {
    const reqData = {
      variables: {
        image_filter: { path: { value: file_path, modifier: "EQUALS" } },
        filter: { per_page: -1 },
      },
      query: `query FindImages($filter: FindFilterType, $image_filter: ImageFilterType){
        findImages(filter: $filter, image_filter: $image_filter) {
          images {
            id
          }
        }
      }`,
    };
    const result = await stash.callGQL(reqData);
    const images = result.data.findImages.images;
    if (images && Array.isArray(images) && images.length > 0) {
      return images;
    }
    return null;
  }

  /**
   * Updates a image with the given image_id and tag_ids.
   * @param {string} image_id - The ID of the image to update.
   * @param {Array<string>} tag_ids - An array of tag IDs to associate with the image.
   * @param {Array<string>} gallery_ids - An array of gallery IDs to associate with the image.
   * @returns {Promise<Object>} - A promise that resolves with the updated image object.
   */
  async function updateImage(image_id, tag_ids, gallery_ids, date) {
    console.log("updating image metadata...");
    const inputData = {
      id: image_id,
      tag_ids: tag_ids,
      gallery_ids: gallery_ids,
    };
    if (typeof date !== "undefined") {
      inputData.date = date;
    }
    const reqData = {
      variables: {
        input: inputData,
      },
      query: `mutation imageUpdate($input: ImageUpdateInput!){
        imageUpdate(input: $input) {
          id
        }
      }`,
    };
    return stash.callGQL(reqData);
  }

  /**
   * Initiate a metadata scan for a given path.
   * @param {string} path - The path to scan.
   * @returns {Promise<Object>} - A promise that resolves with the scan result.
   */
  async function scanMetaData(path) {
    const reqData = {
      variables: {
        input: { paths: [path] },
      },
      query: `mutation MetadataScan($input:ScanMetadataInput!) {
          metadataScan(input: $input)
        }`,
    };
    const result = await stash.callGQL(reqData);
    return result.data.metadataScan;
  }

  async function findJob(job_id) {
    const reqData = {
      variables: {
        input: {
          id: job_id,
        },
      },
      query: `query FindJob($input: FindJobInput!) {
        findJob(input: $input) {
          id
          status
          progress
        }
      }`,
    };
    const results = await stash.callGQL(reqData);
    return results.data.findJob;
  }

  /**
   * Polls a job until it reaches an end state.
   * @param {string} job_id - The ID of the job to poll.
   * @returns {Promise<Object>} - A promise that resolves with the job object.
   */
  async function pollJobQueue(job_id) {
    return new Promise(async (resolve, reject) => {
      let retries = 1;
      while (true) {
        const delay = 2 * retries * 100;
        await new Promise((r) => setTimeout(r, delay));
        retries++;

        const job = await findJob(job_id),
          errorStates = ["FAILED", "CANCELLED"];
        if (job.status === "FINISHED") {
          resolve(job);
          break;
        } else if (errorStates.includes(job.status)) {
          reject(new Error("Job failed."));
          break;
        }

        if (retries >= 20) {
          reject(new Error("Job timed out."));
          break;
        }
      }
    });
  }

  /**
   * Captures a frame from the video player.
   * @param {Object} scene - The scene object.
   * @returns {Promise<Object>} - A promise that resolves with the image path.
   */
  async function captureFrame(scene) {
    return new Promise(async (resolve, reject) => {
      const video = document.getElementById("VideoJsPlayer"),
        reqTime = Date.now();

      if (scene && video && video.player) {
        const framerate = scene.files[0].frame_rate;
        const scene_id = scene.id;
        const player = video.player;
        const currentTime = player.currentTime();

        if (typeof currentTime === "number") {
          const frame_idx = Math.floor(currentTime * framerate);
          const task = "Capture Frame";
          const operation = "captureFrame";
          const payload = [
            { key: "name", value: { str: operation } },
            { key: "mode", value: { str: operation } },
            { key: "scene_id", value: { str: `${scene_id}` } },
            { key: "frame_idx", value: { str: `${frame_idx}` } },
          ];

          const prefix = `[Plugin / ImageCapture] ${operation} =`;

          try {
            await stash.runPluginTask("imagecapture", task, payload);
            // Poll logs until plugin task output appears
            pollLogsForMessage(prefix, "Info", reqTime)
              .then((result) => resolve(JSON.parse(result)))
              .catch(() =>
                pollLogsForMessage(prefix, "Info", reqTime)
                  .then((result) => resolve(JSON.parse(result)))
                  .catch((error) => reject(error))
              );
          } catch (error) {
            reject(error);
          }
        } else {
          reject(new Error("Current time is not a number"));
        }
      } else {
        reject(new Error("Invalid scene or video player"));
      }
    });
  }

  /**
   * Polls the logs for a message with the given prefix and level.
   * @param {string} prefix - The prefix of the message to search for.
   * @param {string} level - The log level of the message to search for.
   * @param {number} reqTime - The time the request was made.
   * @returns {Promise<string>} - A promise that resolves with the message.
   */
  async function pollLogsForMessage(prefix, level, reqTime) {
    reqTime = typeof reqTime !== "undefined" ? reqTime : Date.now();
    const reqData = {
      variables: {},
      query: `query Logs {
          logs {
              time
              level
              message
          }
      }`,
    };
    await new Promise((r) => setTimeout(r, 500));
    let retries = 0;
    while (true) {
      const delay = 2 ** retries * 100;
      await new Promise((r) => setTimeout(r, delay));
      retries++;

      const logs = await stash.callGQL(reqData);
      for (const log of logs.data.logs) {
        if (log.level == level) {
          const logTime = Date.parse(log.time);
          if (logTime > reqTime && log.message.startsWith(prefix)) {
            return log.message.replace(prefix, "").trim();
          }
        }
      }

      if (retries >= 20) {
        break;
      }
    }
    throw `Poll logs failed for message: ${prefix}`;
  }

  /**
   * Handles the metadata update for an image.
   * @param {Object} scene - Scene object
   * @param {string} image_path - The path of the image to update.
   * @returns {Promise<Object>} - A promise that resolves with the updated image object.
   */
  async function handleImageUpdate(scene, image_path) {
    return new Promise(async (resolve, reject) => {
      findImagesByPath(image_path)
        .then(function (images) {
          if (images && Array.isArray(images) && images.length > 0) {
            const image_id = images[0].id,
              { date, tags, galleries } = scene;
            updateImage(image_id, tags, galleries, date).then(function (r) {
              resolve(r);
            });
          } else {
            reject(new Error("image not found."));
          }
        })
        .catch(function (err) {
          console.log(err);
          reject(new Error("image update failed."));
        });
    });
  }

  /**
   * Event handler for the capture button.
   * @param {Event} e - The event object
   * @returns {void}
   */
  function onTriggerCapture(e) {
    e.preventDefault();
    const [_, scene_id] = getScenarioAndID();
    getSceneMetadata(scene_id).then(function (scene) {
      if (scene) {
        const capStart = Date.now();
        display_notice();
        captureFrame(scene, capStart)
          .then(function (response) {
            if (response && response.result) {
              const image_path = response.result,
                image_dir = image_path.split("/").slice(0, -1).join("/") + "/";
              scanMetaData(image_dir)
                .then((job_id) => {
                  pollJobQueue(job_id)
                    .then((job) => {
                      window.addEventListener("beforeunload", warnUnload);
                      handleImageUpdate(scene, image_path)
                        .then(() => {
                          removeWarn();
                          close_modal();
                        })
                        .catch((e) => {
                          console.log(e);
                          close_modal();
                          display_error("failed meta update, retrying...");
                          console.log("failed meta update, retrying...");
                          handleImageUpdate(scene, image_path)
                            .then(() => {
                              removeWarn();
                              close_modal();
                            })
                            .catch((e) => {
                              close_modal();
                              display_error(e);
                              console.log(e);
                              removeWarn();
                            });
                        });
                    })
                    .catch((e) => {
                      console.log("Did not detect scan completion.");
                      close_modal();
                      display_error("Did not detect scan completion.");
                      removeWarn();
                    });
                })
                .catch((e) => {
                  console.log(e);
                  close_modal();
                  display_error(e);
                });
            } else {
              console.log("failed capture attempt.");
              close_modal();
              display_error("failed capture attempt.");
              removeWarn();
            }
          })
          .catch(function (e) {
            console.log(e);
            close_modal();
            display_error(e);
            removeWarn();
          });
      } else {
        console.log("scene not found.");
        close_modal();
        display_error("scene not found.");
        removeWarn();
      }
    });
  }

  function init() {
    let btnGrp = ".scene-toolbar-group:nth-child(2)";
    let wrapper = ".VideoPlayer .video-wrapper";

    $(function () {
      if (!document.querySelector("#imagecapture-styles")) {
        let css = buildStyles(ui.styles);
        $('<style id="imagecapture-styles"></style>')
          .text(css)
          .appendTo("head");
      }
    });

    waitForElm(wrapper).then(async ($el) => {
      if (!document.querySelector("#imagecapture")) {
        const link = document.createElement("a");

        waitForElm(btnGrp).then(async ($btnGrpEl) => {
          if (!document.querySelector("#imagecapture")) {
            const btn = document.createElement("button");
            const spn = document.createElement("span");
            btn.setAttribute("id", "imagecapture");
            btn.setAttribute("class", "minimal btn btn-secondary");
            btn.setAttribute("title", "Take Screen Shot");
            const svg = ui.templates.icons.camera;
            btn.innerHTML = svg;
            spn.appendChild(btn);
            $btnGrpEl.prepend(spn);
            btn.addEventListener("click", onTriggerCapture);
          }
        });
      }
    });
  }

  stash.addEventListener("stash:page:scene", init);
})();
